/**
 * Autonomous Graduation Engine for Task 2: The Inbox Agent.
 * Rules:
 * - "The same kind": Email category / intent cluster.
 * - "Without changing": Levenshtein similarity >= 0.95 (or exact approval).
 * - "Graduation": 20 consecutive unchanged sends promotes category to AUTO_SEND_ELIGIBLE.
 * - "Demotion": Any human override, edit below threshold, or negative feedback immediately
 *   resets the streak to 0 and reverts status to HUMAN_REVIEW_REQUIRED.
 */

import * as fs from 'fs';
import * as path from 'path';
import { EmailCategory, GraduationState } from './types';

export class GraduationEngine {
  private filePath: string;
  private states: Map<EmailCategory, GraduationState> = new Map();
  private graduationThreshold: number = 20;
  private readonly SIMILARITY_THRESHOLD = 0.95;

  constructor(storageDir: string = path.join(__dirname, '..', 'data')) {
    if (!fs.existsSync(storageDir)) {
      fs.mkdirSync(storageDir, { recursive: true });
    }
    this.filePath = path.join(storageDir, 'graduation_store.json');
    this.initializeDefaultStates();
    this.load();
  }

  public setThreshold(newThreshold: number): number {
    this.graduationThreshold = Math.max(1, newThreshold);
    for (const state of this.states.values()) {
      state.threshold = this.graduationThreshold;
      if (state.consecutive_unchanged >= this.graduationThreshold) {
        state.auto_send_eligible = true;
        state.status = 'AUTO_SEND_ELIGIBLE';
      }
    }
    this.save();
    console.log(`[GraduationEngine] ⚙️ Updated consecutive unedited threshold X to: ${this.graduationThreshold}`);
    return this.graduationThreshold;
  }

  public getThreshold(): number {
    return this.graduationThreshold;
  }

  private initializeDefaultStates(): void {
    const categories: { cat: EmailCategory; label: string; conf: number }[] = [
      // 9 Core Categories from PDF Spec
      { cat: 'Filters', label: 'Filters & Search Facets', conf: 0.94 },
      { cat: 'Home Page', label: 'Home Page & Hero Layout', conf: 0.92 },
      { cat: 'Domain Management', label: 'Domain Management & DNS/SSL', conf: 0.95 },
      { cat: 'Header', label: 'Header & Logo Navigation', conf: 0.93 },
      { cat: 'Main Menu', label: 'Main Menu & Navbar Dropdowns', conf: 0.91 },
      { cat: 'Footer', label: 'Footer & Copyright Widgets', conf: 0.96 },
      { cat: 'General Settings', label: 'General Settings & Locales', conf: 0.95 },
      { cat: 'Design Settings', label: 'Design Settings, CSS & Themes', conf: 0.93 },
      { cat: 'Managers', label: 'Managers & Staff Admin Accounts', conf: 0.90 },
      // Standard intent clusters
      { cat: 'how_to', label: 'How-To & Technical Inquiries', conf: 0.92 },
      { cat: 'new_project', label: 'New Project Scoping', conf: 0.88 },
      { cat: 'refund', label: 'Billing, Refunds & Cancellations', conf: 0.96 },
      { cat: 'complaint', label: 'Urgent Issues & Complaints', conf: 0.89 },
      { cat: 'quote', label: 'Quotes & Pricing', conf: 0.90 },
      { cat: 'follow_up', label: 'Ticket & Work Follow-ups', conf: 0.91 }
    ];

    for (const { cat, label, conf } of categories) {
      this.states.set(cat, {
        category: cat,
        category_label: label,
        confidence_score: conf,
        consecutive_unchanged: 0,
        threshold: this.graduationThreshold,
        total_approved: 0,
        total_auto_sent: 0,
        auto_send_eligible: false,
        status: 'HUMAN_REVIEW_REQUIRED',
        last_updated: new Date().toISOString()
      });
    }
  }

  load(): void {
    if (fs.existsSync(this.filePath)) {
      try {
        const raw = fs.readFileSync(this.filePath, 'utf-8');
        const data = JSON.parse(raw);
        for (const item of data) {
          this.states.set(item.category as EmailCategory, item);
        }
      } catch (err) {
        console.error('[GraduationEngine] Error loading graduation state:', err);
      }
    }
  }

  save(): void {
    const list = Array.from(this.states.values());
    fs.writeFileSync(this.filePath, JSON.stringify(list, null, 2), 'utf-8');
  }

  getState(category: EmailCategory): GraduationState {
    const state = this.states.get(category);
    if (!state) {
      throw new Error(`Unknown category: ${category}`);
    }
    return state;
  }

  getAllStates(): GraduationState[] {
    return Array.from(this.states.values());
  }

  /**
   * Evaluates an email approval or edit event.
   * Updates graduation streak or triggers demotion.
   */
  processEmailSent(category: EmailCategory, similarity: number): GraduationState {
    const state = this.getState(category);
    state.total_approved += 1;
    state.last_updated = new Date().toISOString();
    if (state.confidence_score === undefined) {
      state.confidence_score = 0.90;
    }

    const isUnchanged = similarity >= this.SIMILARITY_THRESHOLD;

    if (isUnchanged) {
      // Increment consecutive unchanged counter
      state.consecutive_unchanged += 1;
      state.confidence_score = Math.min(0.99, Number((state.confidence_score + 0.01).toFixed(2)));

      // Check for graduation against configurable threshold X
      if (state.consecutive_unchanged >= state.threshold) {
        if (!state.auto_send_eligible) {
          console.log(`[GraduationEngine] 🎓 CATEGORY GRADUATED! ${category} reached ${state.consecutive_unchanged} consecutive unchanged approvals. Status: AUTO_SEND_ELIGIBLE.`);
        }
        state.auto_send_eligible = true;
        state.status = 'AUTO_SEND_ELIGIBLE';
      }
    } else {
      // Quality drop / Human edited the draft -> DEMOTION
      state.confidence_score = Math.max(0.70, Number((state.confidence_score - 0.03).toFixed(2)));
      if (state.auto_send_eligible || state.consecutive_unchanged > 0) {
        const prevStreak = state.consecutive_unchanged;
        state.consecutive_unchanged = 0;
        state.auto_send_eligible = false;
        state.status = 'HUMAN_REVIEW_REQUIRED';
        state.last_demotion_reason = `Human edited draft (similarity ${(similarity * 100).toFixed(1)}% < ${(this.SIMILARITY_THRESHOLD * 100)}%). Reset streak from ${prevStreak} to 0.`;
        console.warn(`[GraduationEngine] ⚠️ DEMOTION TRIGGERED on category ${category}: ${state.last_demotion_reason}`);
      }
    }

    this.save();
    return state;
  }

  /**
   * Explicit demotion trigger when a customer complains or quality check fails.
   */
  demote(category: EmailCategory, reason: string): GraduationState {
    const state = this.getState(category);
    state.consecutive_unchanged = 0;
    state.auto_send_eligible = false;
    state.status = 'HUMAN_REVIEW_REQUIRED';
    state.last_demotion_reason = reason;
    state.last_updated = new Date().toISOString();
    this.save();
    console.warn(`[GraduationEngine] ⚠️ FORCED DEMOTION on ${category}: ${reason}`);
    return state;
  }

  /**
   * Helper to check if an email can be auto-sent without human review.
   */
  canAutoSend(category: EmailCategory, confidence: number): boolean {
    const state = this.getState(category);
    return state.auto_send_eligible && confidence >= 0.90;
  }

  recordAutoSend(category: EmailCategory): void {
    const state = this.getState(category);
    state.total_auto_sent += 1;
    this.save();
  }
}

export const graduationEngine = new GraduationEngine();
