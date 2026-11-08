import { createServer, IncomingMessage, ServerResponse } from 'node:http';
import { readFile } from 'node:fs/promises';
import { existsSync, readFileSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';
import { Mistral } from '@mistralai/mistralai';

function loadEnvFile(path: string): void {
  if (!existsSync(path)) return;
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq <= 0) continue;
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (process.env[key] === undefined) process.env[key] = value;
  }
}

loadEnvFile(join(__dirname, '..', '.env'));

const PORT = Number(process.env.PORT ?? 3000);
const MODEL = 'mistral-small-latest';
const MAX_BODY_BYTES = 64 * 1024;
const MAX_MESSAGES = 50;
const MAX_CONTENT_LENGTH = 4000;

if (!process.env.MISTRAL_API_KEY) {
  console.error('Erreur : MISTRAL_API_KEY est manquante.');
  console.error('Copiez .env.example en .env et renseignez votre clé : cp .env.example .env');
  process.exit(1);
}

const client = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });

type ChatRole = 'system' | 'user' | 'assistant';
interface ChatMessage {
  role: ChatRole;
  content: string;
}

const MIME_TYPES: Record<string, string> = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
};

const publicDir = join(__dirname, '..', 'public');

function sendJson(res: ServerResponse, status: number, data: unknown): void {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    let size = 0;
    req.on('data', (chunk: Buffer) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        reject(new Error('Payload trop volumineux'));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

function parseMessages(raw: string): ChatMessage[] {
  const parsed = JSON.parse(raw);
  const messages = parsed?.messages;
  if (!Array.isArray(messages) || messages.length === 0 || messages.length > MAX_MESSAGES) {
    throw new Error('messages invalide');
  }
  for (const m of messages) {
    if (
      typeof m?.role !== 'string' ||
      !['system', 'user', 'assistant'].includes(m.role) ||
      typeof m?.content !== 'string' ||
      m.content.length === 0 ||
      m.content.length > MAX_CONTENT_LENGTH
    ) {
      throw new Error('messages invalide');
    }
  }
  return messages as ChatMessage[];
}

function extractText(content: unknown): string {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    return content
      .map((chunk) =>
        chunk && typeof chunk === 'object' && 'text' in chunk && typeof (chunk as { text: unknown }).text === 'string'
          ? (chunk as { text: string }).text
          : '',
      )
      .join('');
  }
  return '';
}

async function handleChat(req: IncomingMessage, res: ServerResponse): Promise<void> {
  let messages: ChatMessage[];
  try {
    messages = parseMessages(await readBody(req));
  } catch {
    sendJson(res, 400, { error: 'Requête invalide : champ "messages" attendu.' });
    return;
  }

  try {
    const response = await client.chat.complete({ model: MODEL, messages });
    const reply = extractText(response.choices?.[0]?.message?.content);
    sendJson(res, 200, { reply });
  } catch (err) {
    console.error('Erreur API Mistral :', err);
    sendJson(res, 502, { error: "Erreur lors de l'appel à l'API Mistral." });
  }
}

async function serveStatic(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? '/', 'http://localhost');
  let pathname = decodeURIComponent(url.pathname);
  if (pathname === '/') pathname = '/index.html';
  const filePath = normalize(join(publicDir, pathname));
  if (!filePath.startsWith(publicDir)) {
    res.writeHead(403).end('Interdit');
    return;
  }
  try {
    const content = await readFile(filePath);
    res.writeHead(200, {
      'Content-Type': MIME_TYPES[extname(filePath)] ?? 'application/octet-stream',
      'Content-Length': content.length,
    });
    res.end(content);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Non trouvé');
  }
}

const server = createServer((req, res) => {
  const url = new URL(req.url ?? '/', 'http://localhost');
  if (req.method === 'POST' && url.pathname === '/api/chat') {
    void handleChat(req, res);
    return;
  }
  if (req.method === 'GET') {
    void serveStatic(req, res);
    return;
  }
  res.writeHead(405, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Méthode non autorisée');
});

server.listen(PORT, () => {
  console.log(`Chat Mistral démarré sur http://localhost:${PORT} (modèle : ${MODEL})`);
});
