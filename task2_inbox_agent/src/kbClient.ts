/**
 * Client for Task 1: The Knowledge Brain API.
 * Communicates with Task 1 strictly via HTTP REST endpoints.
 */

import { KBArticleCitation } from './types';

export class KnowledgeBrainClient {
  private apiUrl: string;

  constructor(apiUrl: string = process.env.TASK1_API_URL || 'http://localhost:8001') {
    this.apiUrl = apiUrl.replace(/\/$/, '');
  }

  /**
   * Queries Task 1 Knowledge Brain API for relevant solution center articles.
   */
  async searchArticles(query: string, topK: number = 3): Promise<KBArticleCitation[]> {
    try {
      const response = await fetch(`${this.apiUrl}/api/v1/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          query: query,
          top_k: topK
        }),
        signal: AbortSignal.timeout(6000)
      });

      if (!response.ok) {
        console.warn(`[KBClient] Knowledge Brain API returned status ${response.status}`);
        return [];
      }

      const data = await response.json() as { results: any[] };
      if (!data.results || !Array.isArray(data.results)) {
        return [];
      }

      return data.results.map((r: any) => ({
        article_id: r.article_id || '',
        title: r.title || 'Brilliant Directories Article',
        url: r.url || 'https://support.brilliantdirectories.com',
        category: r.category || 'General',
        folder: r.folder || 'Documentation',
        snippet: r.snippet || '',
        score: typeof r.score === 'number' ? r.score : 0.5
      }));
    } catch (err: any) {
      console.warn(`[KBClient] Unable to connect to Knowledge Brain at ${this.apiUrl}: ${err.message}. Using cache if available.`);
      return [];
    }
  }

  /**
   * Health check to verify Task 1 is reachable.
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.apiUrl}/api/v1/health`, {
        signal: AbortSignal.timeout(3000)
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const kbClient = new KnowledgeBrainClient();
