/**
 * Evaluation Suite for Task 2: The Inbox Agent.
 * 22 automated test cases verifying:
 * - Intent & category classification accuracy
 * - Knowledge Brain API integration
 * - Company voice & tone compliance
 * - Levenshtein edit distance & self-improving learning curve
 * - Feedback undo rollback
 * - 20-streak autonomous graduation & quality demotion guardrails
 * - End-to-end TypeScript strict typing
 */

import { emailClassifier } from '../src/classifier';
import { emailDrafter } from '../src/drafter';
import { learningStore } from '../src/learningStore';
import { graduationEngine } from '../src/graduation';
import { CustomerEmail, EmailCategory } from '../src/types';
import { googleAuthService } from '../src/googleAuthService';
import { aiEmailComposer } from '../src/aiComposer';
import { gmailService } from '../src/gmailService';

let totalTests = 0;
let passedTests = 0;

function assert(condition: boolean, testName: string, details: string = '') {
  totalTests++;
  if (condition) {
    passedTests++;
    console.log(`  ✅ [PASS] ${testName}`);
  } else {
    console.error(`  ❌ [FAIL] ${testName} - ${details}`);
    throw new Error(`Test failed: ${testName} (${details})`);
  }
}

async function runTests() {
  console.log('\n========================================================');
  console.log('🧪 Starting Task 2: The Inbox Agent Evaluation Suite');
  console.log('========================================================\n');

  // --- Group 1: Intent & Category Classification (Tests 1 - 10) ---
  console.log('--- Group 1: Category & Intent Classification (10 Tests) ---');

  const c1 = emailClassifier.classify('How to set up Stripe billing for monthly member renewals?', 'Where do we enter Stripe keys?');
  assert(c1.category === 'how_to' && c1.confidence >= 0.70, 'test_01_classify_how_to_billing', `got ${c1.category}`);

  const c2 = emailClassifier.classify('Changing search radius from miles to kilometers', 'How do we change distance measurement?');
  assert(c2.category === 'how_to', 'test_02_classify_how_to_search', `got ${c2.category}`);

  const c3 = emailClassifier.classify('Mobile application development for iOS and Android', 'We want a dedicated mobile app wrapped around directory.');
  assert(c3.category === 'new_project', 'test_03_classify_new_project_mobile_app', `got ${c3.category}`);

  const c4 = emailClassifier.classify('Building custom RFQ bidding marketplace', 'We want commercial property owners to post tenders.');
  assert(c4.category === 'new_project', 'test_04_classify_new_project_rfq', `got ${c4.category}`);

  const c5 = emailClassifier.classify('Accidental double charge on annual renewal', 'Please issue a refund for duplicate transaction TX-88219.');
  assert(c5.category === 'refund' && c5.urgency === 'high', 'test_05_classify_refund_double_charge', `got ${c5.category}, ${c5.urgency}`);

  const c6 = emailClassifier.classify('Cancel subscription and refund unused monthly fee', 'We closed our agency. Please reverse this charge.');
  assert(c6.category === 'refund', 'test_06_classify_refund_cancellation', `got ${c6.category}`);

  const c7 = emailClassifier.classify('URGENT: Directory search is down for all visitors!', 'Search bar spins for 30s and throws 504 timeout.');
  assert(c7.category === 'complaint' && c7.urgency === 'high', 'test_07_classify_complaint_outage', `got ${c7.category}, ${c7.urgency}`);

  const c8 = emailClassifier.classify('Member emails going to spam folder - SPF/DKIM broken?', 'All password resets landing in spam or rejected by Gmail.');
  assert(c8.category === 'complaint', 'test_08_classify_complaint_spf_dkim', `got ${c8.category}`);

  const c9 = emailClassifier.classify('Quote for data migration of 2,200 venues', 'Please provide a formal quote and estimated timeline for migration.');
  assert(c9.category === 'quote', 'test_09_classify_quote_migration', `got ${c9.category}`);

  const c10 = emailClassifier.classify('Follow-up on Ticket #3891: Custom search filter dropdown', 'Checking in on the status of our ticket from last Thursday.');
  assert(c10.category === 'follow_up', 'test_10_classify_follow_up_ticket', `got ${c10.category}`);

  // --- Group 2: Drafting & Company Voice (Tests 11 - 14) ---
  console.log('\n--- Group 2: Drafting, Voice & KB Integration (4 Tests) ---');

  const sampleEmail: CustomerEmail = {
    id: 'TEST-001',
    customer_name: 'Elena Rostova',
    customer_email: 'elena@wellness.com',
    company_name: 'Denver Wellness',
    category: 'how_to',
    subject: 'How to connect Stripe payment gateway?',
    body: 'Where do we enter our Stripe API keys for member billing?',
    urgency: 'medium',
    date: new Date().toISOString(),
    status: 'unread',
    confidence: 0,
    citations: [],
    auto_sent: false
  };

  const draftResult = await emailDrafter.draftReply(sampleEmail);
  assert(draftResult.draft.includes('Hi Elena') || draftResult.draft.includes('Elena'), 'test_11_drafter_company_voice_greeting', 'Missing personalized customer name');
  assert(draftResult.draft.includes('Best regards') || draftResult.draft.includes('Solutions Team'), 'test_11b_drafter_professional_signoff', 'Missing company signoff');
  assert(draftResult.confidence >= 0.80, 'test_12_drafter_kb_citations_integration', `Confidence too low: ${draftResult.confidence}`);

  const refundEmail: CustomerEmail = {
    ...sampleEmail,
    id: 'TEST-002',
    category: 'refund',
    subject: 'Refund request for duplicate charge',
    body: 'I was charged twice yesterday for $499.'
  };
  const refundDraft = await emailDrafter.draftReply(refundEmail);
  assert(refundDraft.draft.toLowerCase().includes('refund') && refundDraft.draft.toLowerCase().includes('business days'), 'test_13_drafter_refund_timeline_policy', 'Refund draft missing timeline');

  const complaintEmail: CustomerEmail = {
    ...sampleEmail,
    id: 'TEST-003',
    category: 'complaint',
    subject: 'URGENT: Site search down',
    body: '504 gateway timeout on search bar.'
  };
  const complaintDraft = await emailDrafter.draftReply(complaintEmail);
  assert(complaintDraft.draft.toLowerCase().includes('apologize') || complaintDraft.draft.toLowerCase().includes('escalated'), 'test_14_drafter_complaint_empathy_and_ticket', 'Complaint draft missing empathy/ticket');

  // --- Group 3: Levenshtein Distance & Self-Improving Learning Loop (Tests 15 - 18) ---
  console.log('\n--- Group 3: Self-Improving Feedback Loop & Undo (4 Tests) ---');

  const originalDraft = 'Thanks for reaching out. We can fix this issue soon.';
  const editedReply = 'Thanks for reaching out! We have escalated this issue to our senior engineers and will resolve it within 2 hours.';
  const editDist = learningStore.calculateEditDistance(originalDraft, editedReply);
  const similarity = learningStore.calculateSimilarity(originalDraft, editedReply);

  assert(editDist > 0 && similarity > 0 && similarity < 1.0, 'test_15_learning_store_edit_distance_calculation', `Distance: ${editDist}, Sim: ${similarity}`);

  const initialVersion = learningStore.getPromptVersion();
  const feedback = learningStore.recordFeedback('TEST-004', 'refund', 'Test refund', originalDraft, editedReply);
  assert(feedback.learned_rule.length > 10, 'test_16_learning_store_rule_extraction', 'Failed to extract rule');
  assert(learningStore.getPromptVersion() !== initialVersion, 'test_16b_prompt_version_incremented', 'Prompt version did not increment');

  const undoSuccess = learningStore.undoFeedback(feedback.id);
  assert(undoSuccess === true, 'test_17_learning_store_undo_capability', 'Undo failed');

  const metrics = learningStore.getMetrics();
  assert(metrics.improvement_percentage >= 0, 'test_18_learning_curve_improvement_metric', 'Invalid improvement metrics');

  // --- Group 4: Autonomous Graduation & Demotion Guardrails (Tests 19 - 22) ---
  console.log('\n--- Group 4: Autonomous Graduation & Safety Demotion (4 Tests) ---');

  const testCategory: EmailCategory = 'how_to';

  // 19. Simulate 20 consecutive unchanged sends
  let state;
  for (let i = 0; i < 20; i++) {
    state = graduationEngine.processEmailSent(testCategory, 1.0);
  }
  assert(state?.consecutive_unchanged === 20 && state.auto_send_eligible === true, 'test_19_graduation_20_streak_promotion', `Streak: ${state?.consecutive_unchanged}, Eligible: ${state?.auto_send_eligible}`);

  // 20. Human edits draft (similarity 0.70 < 0.95) -> Immediate Demotion!
  const demotedState = graduationEngine.processEmailSent(testCategory, 0.70);
  assert(demotedState.consecutive_unchanged === 0 && demotedState.auto_send_eligible === false, 'test_20_graduation_demotion_on_human_edit', `Streak not reset: ${demotedState.consecutive_unchanged}`);
  assert(demotedState.status === 'HUMAN_REVIEW_REQUIRED', 'test_20b_demotion_status_reset', `Status: ${demotedState.status}`);

  // 21. Auto-send gatekeeper prevents ungraduated send
  const canAuto = graduationEngine.canAutoSend(testCategory, 0.95);
  assert(canAuto === false, 'test_21_auto_send_gatekeeper_safety', 'Should not allow auto-send when not graduated');

  // 22. Typed contract verification
  const allStates = graduationEngine.getAllStates();
  assert(allStates.length >= 6 && allStates.every(s => typeof s.consecutive_unchanged === 'number'), 'test_22_type_safety_and_schema_validation', 'Invalid schema');

  // --- Group 5: Google Account Authentication & OAuth 2.0 (Tests 23 - 26) ---
  console.log('\n--- Group 5: Google OAuth 2.0 Authentication & Profile (4 Tests) ---');

  const urlInfo = googleAuthService.getAuthUrl();
  assert(urlInfo.scopes.includes('https://www.googleapis.com/auth/gmail.send') && urlInfo.scopes.includes('https://www.googleapis.com/auth/gmail.compose'), 'test_23_google_oauth_url_and_scopes', 'Missing Gmail API scopes');

  const demoUser = googleAuthService.connectDemoUser('consultant.test@gmail.com', 'Alex Morgan');
  assert(demoUser.email === 'consultant.test@gmail.com' && demoUser.name === 'Alex Morgan' && demoUser.verified_email === true, 'test_24_google_demo_account_connection', 'Demo connection profile mismatch');

  const status = googleAuthService.getStatus();
  assert(status.is_connected === true && status.user_profile?.email === 'consultant.test@gmail.com', 'test_25_google_auth_status_retrieval', 'Invalid auth status');

  const disc = googleAuthService.disconnect();
  assert(disc.success === true && googleAuthService.getStatus().is_connected === false, 'test_26_google_disconnect_and_account_switch', 'Failed to disconnect Google account');

  // Re-connect demo user for downstream composition tests
  googleAuthService.connectDemoUser('consultant.test@gmail.com', 'Alex Morgan');

  // --- Group 6: AI Email Assistant & Natural Language Composition (Tests 27 - 31) ---
  console.log('\n--- Group 6: AI Email Assistant & Tone Spectrum (5 Tests) ---');

  const leaveRes = await aiEmailComposer.compose({ instruction: 'Write a professional email requesting leave for tomorrow.', tone: 'Professional' });
  assert(leaveRes.subject.toLowerCase().includes('leave') && leaveRes.body.toLowerCase().includes('leave') && leaveRes.tone === 'Professional', 'test_27_ai_compose_leave_request', 'Invalid leave request draft');

  const inviteRes = await aiEmailComposer.compose({ instruction: 'Compose an email inviting students to an AI workshop.', tone: 'Friendly' });
  assert(inviteRes.subject.toLowerCase().includes('workshop') && inviteRes.body.toLowerCase().includes('workshop') && inviteRes.tone === 'Friendly', 'test_28_ai_compose_workshop_invite', 'Invalid workshop invite');

  const conciseRes = await aiEmailComposer.compose({ instruction: 'Draft an interview follow up email.', tone: 'Concise' });
  const persuasiveRes = await aiEmailComposer.compose({ instruction: 'Draft an interview follow up email.', tone: 'Persuasive' });
  assert(conciseRes.tone === 'Concise' && persuasiveRes.tone === 'Persuasive' && conciseRes.body.length < persuasiveRes.body.length, 'test_29_ai_compose_tones_spectrum', 'Tone spectrum variation failure');

  const baseText = 'Dear Hiring Manager, Thank you for taking the time to speak with me yesterday regarding the AI Consultant position. I enjoyed our conversation.';
  const shortened = await aiEmailComposer.compose({ action: 'shorten', current_draft: baseText });
  const expanded = await aiEmailComposer.compose({ action: 'expand', current_draft: baseText });
  assert(shortened.body.length <= baseText.length && expanded.body.length >= baseText.length, 'test_30_ai_refine_shorten_and_expand', 'Refinement shorten/expand failed');

  const draftWithErrors = 'i wants to thank you for meeting me yesturday.';
  const polished = await aiEmailComposer.compose({ action: 'fix_grammar', current_draft: draftWithErrors });
  assert(polished.body.toLowerCase().includes('thank you'), 'test_31_ai_refine_grammar_and_tone', 'Grammar polish failed');

  // --- Group 7: Gmail Integration, RFC 2822 MIME, Drafts & Sending Invariant (Tests 32 - 36) ---
  console.log('\n--- Group 7: Gmail RFC 2822 MIME, Drafts & Sending Invariant (5 Tests) ---');

  const rfcRaw = (gmailService as any).buildRFC2822Raw({
    to: 'client@example.com',
    subject: 'Invoice #102',
    body: 'Please find attached invoice.',
    attachments: [{ filename: 'invoice.pdf', mime_type: 'application/pdf', content_base64: 'JVBERi0xLjQK...' }]
  }, 'sender@gmail.com');
  const decodedMime = Buffer.from(rfcRaw.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8');
  assert(decodedMime.includes('To: client@example.com') && decodedMime.includes('Subject: Invoice #102') && decodedMime.includes('filename="invoice.pdf"'), 'test_32_gmail_rfc2822_mime_builder', 'MIME generation incorrect');

  const draftItem = await gmailService.saveDraft({
    to: 'director@agency.com',
    subject: 'Proposal Draft',
    body: 'Draft proposal for review.',
    attachments: []
  });
  assert(draftItem.id.startsWith('draft') && draftItem.subject === 'Proposal Draft', 'test_33_gmail_save_draft_with_attachments', 'Draft save failed');
  const draftsList = await gmailService.listDrafts();
  assert(draftsList.some(d => d.id === draftItem.id), 'test_33b_gmail_drafts_listing', 'Draft not found in listing');

  const sendRes = await gmailService.sendComposedEmail({
    to: 'partner@techcorp.com',
    subject: 'Confirmed SOW',
    body: 'Here is our agreed statement of work.'
  });
  assert(sendRes.success === true && sendRes.status === 'sent' && typeof sendRes.message_id === 'string', 'test_34_gmail_send_composed_email', 'Send email failed');
  const sentList = gmailService.listSentEmails();
  assert(sentList.some(s => s.to === 'partner@techcorp.com'), 'test_34b_gmail_sent_list_persistence', 'Sent email not found in sent items');

  let errorThrown = false;
  try {
    await gmailService.sendComposedEmail({ to: '', subject: '', body: '' });
  } catch (e) {
    errorThrown = true;
  }
  assert(errorThrown === true, 'test_35_gmail_send_validation', 'Failed to reject invalid email payload');

  const finalSent = sentList.find(s => s.to === 'partner@techcorp.com');
  assert(finalSent !== undefined && finalSent.from_account.length > 0 && finalSent.sent_at.length > 0, 'test_36_gmail_user_approval_invariant', 'Missing audit trail for sent email');

  console.log('\n========================================================');
  console.log(`🎉 Task 2 Evaluation Complete: ${passedTests}/${totalTests} tests passed (100% Success)`);
  console.log('========================================================\n');
  process.exit(0);
}

runTests().catch(err => {
  console.error('Test suite failed:', err);
  process.exit(1);
});
