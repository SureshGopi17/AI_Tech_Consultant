/**
 * Loads the 50 customer emails into Task 2 Inbox Agent.
 */

import * as fs from 'fs';
import * as path from 'path';
import { CustomerEmail } from './types';

export function loadSeedEmails(): CustomerEmail[] {
  // Search path relative to project root
  const candidates = [
    path.join(__dirname, '..', '..', 'shared', 'data', 'emails_50.json'),
    path.join(process.cwd(), 'shared', 'data', 'emails_50.json')
  ];

  for (const filePath of candidates) {
    if (fs.existsSync(filePath)) {
      try {
        const raw = fs.readFileSync(filePath, 'utf-8');
        const list = JSON.parse(raw);
        console.log(`[SeedData] Loaded ${list.length} customer emails from ${filePath}`);
        return list.map((item: any) => ({
          ...item,
          status: 'unread',
          confidence: 0.0,
          citations: [],
          auto_sent: false
        }));
      } catch (err) {
        console.error(`[SeedData] Error parsing ${filePath}:`, err);
      }
    }
  }

  console.warn('[SeedData] Could not find emails_50.json. Returning empty list.');
  return [];
}
