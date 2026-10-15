/**
 * Express Server for Task 2: The Inbox Agent.
 * Strict TypeScript, end-to-end typed APIs, self-improving feedback loop,
 * and autonomous graduation management.
 */

import express, { Request, Response } from 'express';
import cors from 'cors';
import * as path from 'path';
import * as dotenv from 'dotenv';
import { CustomerEmail, EmailCategory } from './types';
import { loadSeedEmails } from './seedData';
import { emailDrafter } from './drafter';
import { learningStore } from './learningStore';
import { graduationEngine } from './graduation';

dotenv.config();

const app = express();
const PORT = parseInt(process.env.PORT_TASK2 || '8002', 10);

app.use(cors());
app.use(express.json());

// In-memory email repository initialized with 50 seed emails
let emails: CustomerEmail[] = loadSeedEmails();

// Serve static frontend
const publicDir = path.join(__dirname, '..', 'public');
app.use(express.static(publicDir));

/**
 * Health check
 */
app.get('/api/v1/health', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'Task 2 - The Inbox Agent',
    total_emails: emails.length,
    active_learning_rules: learningStore.getActiveRules().length,
    prompt_version: learningStore.getPromptVersion()
  });
});

/**
 * List customer emails with optional filtering
 */
app.get('/api/v1/emails', (req: Request, res: Response) => {
  const { category, status, urgency } = req.query;
  let filtered = [...emails];

  if (category) {
    filtered = filtered.filter(e => e.category === category);
  }
  if (status) {
    filtered = filtered.filter(e => e.status === status);
  }
  if (urgency) {
    filtered = filtered.filter(e => e.urgency === urgency);
  }

  res.json({
    emails: filtered,
    total: filtered.length
  });
});

/**
 * Get email details
 */
app.get('/api/v1/emails/:id', (req: Request, res: Response) => {
  const email = emails.find(e => e.id === req.params.id);
  if (!email) {
    res.status(404).json({ error: 'Email not found' });
    return;
  }
  res.json(email);
});

/**
 * Draft reply for an email
 */
app.post('/api/v1/emails/:id/draft', async (req: Request, res: Response) => {
  const email = emails.find(e => e.id === req.params.id);
  if (!email) {
    res.status(404).json({ error: 'Email not found' });
    return;
  }

  try {
    const draftRes = await emailDrafter.draftReply(email);
    email.drafted_reply = draftRes.draft;
    email.confidence = draftRes.confidence;
    email.citations = draftRes.citations;
    email.status = 'drafted';

    res.json({
      email,
      draft_result: draftRes
    });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * Approve draft as-is (1 click send)
 */
app.post('/api/v1/emails/:id/approve', (req: Request, res: Response) => {
  const email = emails.find(e => e.id === req.params.id);
  if (!email) {
    res.status(404).json({ error: 'Email not found' });
    return;
  }

  if (!email.drafted_reply) {
    res.status(400).json({ error: 'Email has not been drafted yet' });
    return;
  }

  email.final_sent_reply = email.drafted_reply;
  email.status = 'approved';
  email.edit_distance = 0;
  email.similarity_ratio = 1.0;
  email.handled_at = new Date().toISOString();

  // Update graduation counter (unchanged send)
  const gradState = graduationEngine.processEmailSent(email.category, 1.0);

  res.json({
    success: true,
    email,
    graduation_state: gradState,
    message: 'Draft approved and sent without edits.'
  });
});

/**
 * Edit draft and send (triggers self-improving learning loop)
 */
app.post('/api/v1/emails/:id/edit', (req: Request, res: Response) => {
  const email = emails.find(e => e.id === req.params.id);
  if (!email) {
    res.status(404).json({ error: 'Email not found' });
    return;
  }

  const { edited_reply } = req.body;
  if (!edited_reply || typeof edited_reply !== 'string') {
    res.status(400).json({ error: 'edited_reply string is required' });
    return;
  }

  const originalDraft = email.drafted_reply || '';
  const feedback = learningStore.recordFeedback(
    email.id,
    email.category,
    email.subject,
    originalDraft,
    edited_reply
  );

  email.final_sent_reply = edited_reply;
  email.status = 'edited_and_sent';
  email.edit_distance = feedback.edit_distance;
  email.similarity_ratio = feedback.similarity_ratio;
  email.handled_at = new Date().toISOString();

  // Update graduation engine (triggers demotion if similarity < 0.95)
  const gradState = graduationEngine.processEmailSent(email.category, feedback.similarity_ratio);

  res.json({
    success: true,
    email,
    feedback,
    graduation_state: gradState,
    message: 'Human edit recorded. Agent has learned from this feedback.'
  });
});

/**
 * Write custom reply and send
 */
app.post('/api/v1/emails/:id/custom', (req: Request, res: Response) => {
  const email = emails.find(e => e.id === req.params.id);
  if (!email) {
    res.status(404).json({ error: 'Email not found' });
    return;
  }

  const { custom_reply } = req.body;
  if (!custom_reply) {
    res.status(400).json({ error: 'custom_reply is required' });
    return;
  }

  const originalDraft = email.drafted_reply || '';
  const feedback = learningStore.recordFeedback(
    email.id,
    email.category,
    email.subject,
    originalDraft,
    custom_reply
  );

  email.final_sent_reply = custom_reply;
  email.status = 'custom_sent';
  email.edit_distance = feedback.edit_distance;
  email.similarity_ratio = feedback.similarity_ratio;
  email.handled_at = new Date().toISOString();

  const gradState = graduationEngine.processEmailSent(email.category, feedback.similarity_ratio);

  res.json({
    success: true,
    email,
    feedback,
    graduation_state: gradState
  });
});

/**
 * Autonomous Graduation Status of all categories
 */
app.get('/api/v1/graduation', (_req: Request, res: Response) => {
  res.json({
    states: graduationEngine.getAllStates()
  });
});

/**
 * Simulate 20 consecutive approvals for testing autonomous graduation
 */
app.post('/api/v1/graduation/:category/simulate-streak', (req: Request, res: Response) => {
  const cat = req.params.category as EmailCategory;
  const count = parseInt(req.body.count || '20', 10);

  let state;
  for (let i = 0; i < count; i++) {
    state = graduationEngine.processEmailSent(cat, 1.0);
  }

  res.json({
    success: true,
    category: cat,
    state,
    message: `Simulated ${count} consecutive unchanged approvals.`
  });
});

/**
 * Explicit demotion trigger for quality testing
 */
app.post('/api/v1/graduation/:category/demote', (req: Request, res: Response) => {
  const cat = req.params.category as EmailCategory;
  const reason = req.body.reason || 'Manual quality override / customer dissatisfaction report';
  const state = graduationEngine.demote(cat, reason);

  res.json({
    success: true,
    state,
    message: `Category ${cat} demoted back to HUMAN_REVIEW_REQUIRED.`
  });
});

/**
 * Learning curve & Feedback metrics
 */
app.get('/api/v1/feedback', (_req: Request, res: Response) => {
  res.json({
    metrics: learningStore.getMetrics(),
    prompt_version: learningStore.getPromptVersion(),
    active_rules: learningStore.getActiveRules(),
    recent_feedbacks: learningStore.getAllFeedbacks().slice(0, 20)
  });
});

/**
 * Undo learned feedback rule
 */
app.post('/api/v1/feedback/undo/:id', (req: Request, res: Response) => {
  const success = learningStore.undoFeedback(req.params.id);
  if (success) {
    res.json({
      success: true,
      message: `Feedback ${req.params.id} undone. Prompt version rolled back.`,
      prompt_version: learningStore.getPromptVersion()
    });
  } else {
    res.status(404).json({ error: 'Feedback ID not found or already inactive' });
  }
});

/**
 * Batch auto-process incoming emails
 */
app.post('/api/v1/emails/auto-process', async (_req: Request, res: Response) => {
  let autoSentCount = 0;
  let draftedCount = 0;

  for (const email of emails.slice(0, 15)) {
    if (email.status === 'unread') {
      const draftRes = await emailDrafter.draftReply(email);
      email.drafted_reply = draftRes.draft;
      email.confidence = draftRes.confidence;
      email.citations = draftRes.citations;

      // Check if eligible for autonomous send
      if (graduationEngine.canAutoSend(email.category, email.confidence)) {
        email.status = 'auto_sent';
        email.auto_sent = true;
        email.final_sent_reply = draftRes.draft;
        email.handled_at = new Date().toISOString();
        graduationEngine.recordAutoSend(email.category);
        autoSentCount++;
      } else {
        email.status = 'drafted';
        draftedCount++;
      }
    }
  }

  res.json({
    success: true,
    auto_sent_count: autoSentCount,
    drafted_count: draftedCount,
    total_processed: autoSentCount + draftedCount
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[Task 2] Inbox Agent running at http://localhost:${PORT}`);
});
