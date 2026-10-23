/**
 * Email Intent & Category Classifier.
 * Maps incoming customer emails into one of the 6 core business categories.
 */

import { EmailCategory, ClassificationResult, UrgencyLevel } from './types';

export class EmailClassifier {
  /**
   * Classifies an incoming customer email based on subject, body, and keywords.
   */
  classify(subject: string, body: string): ClassificationResult {
    const combined = `${subject} ${body}`.toLowerCase();

    // 1. Complaint / Outage keywords
    const complaintMatches = ['urgent', 'down', 'outage', 'broken', 'spin', 'timeout', '504', 'spam', 'bug', 'lagging', 'failing', 'unusable', 'slow support'];
    const complaintScore = complaintMatches.filter(w => combined.includes(w)).length;

    // 2. Refund / Cancellation keywords
    const refundMatches = ['refund', 'cancel', 'cancellation', 'double charge', 'charged twice', 'billing dispute', 'reverse this charge', 'prorated', 'vat invoice'];
    const refundScore = refundMatches.filter(w => combined.includes(w)).length;

    // 3. Follow-up keywords
    const followUpMatches = ['follow-up', 'follow up', 'following up', 'status update', 'checking in', 'ticket #', 'staging build', 'ready for our review'];
    const followUpScore = followUpMatches.filter(w => combined.includes(w)).length;

    // 4. Quote / Retainer keywords
    const quoteMatches = ['quote', 'how much', 'pricing for', 'retainer packages', 'estimate hours', 'formal quote'];
    const quoteScore = quoteMatches.filter(w => combined.includes(w)).length;

    // 5. New Project keywords
    const newProjectMatches = [
      'new project', 'redesign', 'custom api', 'mobile application', 'mobile app',
      'rfq', 'bidding', 'marketplace', 'tender', 'multilingual', 'lookbook',
      'migration from', 'turnkey', 'build', 'develop a custom', 'integration with salesforce'
    ];
    const newProjectScore = newProjectMatches.filter(w => combined.includes(w)).length;

    // 6. How-to keywords
    const howToMatches = ['how to', 'how do we', 'where do we', 'can i', 'guide us', 'setting up', 'configuring', 'steps to', 'where is the setting'];
    const howToScore = howToMatches.filter(w => combined.includes(w)).length;

    let category: EmailCategory = 'how_to';
    let maxScore = howToScore;

    if (complaintScore > maxScore && complaintScore >= 2) {
      category = 'complaint';
      maxScore = complaintScore;
    }
    if (refundScore > maxScore && refundScore >= 1) {
      category = 'refund';
      maxScore = refundScore;
    }
    if (followUpScore > maxScore && followUpScore >= 1) {
      category = 'follow_up';
      maxScore = followUpScore;
    }
    if (newProjectScore > maxScore && newProjectScore >= 1) {
      category = 'new_project';
      maxScore = newProjectScore;
    }
    if (quoteScore > maxScore && quoteScore >= 1) {
      category = 'quote';
      maxScore = quoteScore;
    }

    // Determine Urgency
    let urgency: UrgencyLevel = 'medium';
    if (category === 'complaint' || combined.includes('urgent') || combined.includes('asap') || combined.includes('immediately')) {
      urgency = 'high';
    } else if (category === 'refund' && (combined.includes('double charge') || combined.includes('charged twice') || combined.includes('duplicate') || combined.includes('dispute'))) {
      urgency = 'high';
    } else if (combined.includes('low priority') || category === 'how_to' && combined.includes('promo')) {
      urgency = 'low';
    }

    // Confidence
    const confidence = Math.min(0.96, 0.70 + (maxScore * 0.08));

    // Determine Label and Parent Setting Type
    let label_name = 'General How-To Inquiry';
    let parent_setting_type = 'General Settings';

    // Prioritize 9 PDF Core Setting Categories:
    // Filters, Home Page, Domain Management, Header, Main Menu, Footer, General Settings, Design Settings, Managers
    if (combined.includes('filter') || combined.includes('radius') || combined.includes('search distance')) {
      parent_setting_type = 'Filters';
      label_name = combined.includes('radius') ? 'Search Distance & Radius Filter' : 'Custom Search Filter & Facets';
    } else if (combined.includes('home page') || combined.includes('homepage') || combined.includes('hero banner') || combined.includes('landing page')) {
      parent_setting_type = 'Home Page';
      label_name = 'Home Page & Hero Banner Configuration';
    } else if (combined.includes('domain') || combined.includes('dns') || combined.includes('ssl') || combined.includes('cname')) {
      parent_setting_type = 'Domain Management';
      label_name = 'Custom Domain & SSL Mapping';
    } else if (combined.includes('header') || combined.includes('logo') || combined.includes('favicon') || combined.includes('top bar')) {
      parent_setting_type = 'Header';
      label_name = 'Header Branding & Top Navigation';
    } else if (combined.includes('main menu') || combined.includes('navbar') || combined.includes('navigation links') || combined.includes('menu')) {
      parent_setting_type = 'Main Menu';
      label_name = 'Main Menu & Dropdown Links Setup';
    } else if (combined.includes('footer') || combined.includes('copyright') || combined.includes('bottom menu')) {
      parent_setting_type = 'Footer';
      label_name = 'Footer Widget & Legal Copyright Links';
    } else if (combined.includes('design settings') || combined.includes('styling') || combined.includes('css') || combined.includes('color') || combined.includes('theme')) {
      parent_setting_type = 'Design Settings';
      label_name = 'Design Settings & Color Theme Styling';
    } else if (combined.includes('manager') || combined.includes('admin account') || combined.includes('sub-account') || combined.includes('permission') || combined.includes('staff')) {
      parent_setting_type = 'Managers';
      label_name = 'Staff Managers & Admin Access Control';
    } else if (category === 'how_to') {
      if (combined.includes('stripe') || combined.includes('billing') || combined.includes('payment')) {
        label_name = 'Stripe Member Billing Setup';
        parent_setting_type = 'General Settings';
      } else if (combined.includes('custom field') || combined.includes('form') || combined.includes('registration')) {
        label_name = 'Custom Registration Form Fields';
        parent_setting_type = 'General Settings';
      } else if (combined.includes('lead')) {
        label_name = 'Automated Lead Routing Rules';
        parent_setting_type = 'General Settings';
      } else if (combined.includes('webhook')) {
        label_name = 'Outbound Webhooks & CRM Sync';
        parent_setting_type = 'General Settings';
      }
    } else if (category === 'refund') {
      label_name = combined.includes('double') || combined.includes('twice') 
        ? 'Duplicate Transaction Refund' 
        : 'Subscription Cancellation & Refund';
      parent_setting_type = 'General Settings';
    } else if (category === 'complaint') {
      label_name = combined.includes('down') || combined.includes('outage') || combined.includes('504')
        ? 'Platform Outage & Downtime Incident'
        : 'Email Delivery & SPF/DKIM Configuration';
      parent_setting_type = 'General Settings';
    } else if (category === 'new_project') {
      label_name = combined.includes('mobile') || combined.includes('ios')
        ? 'Mobile Application Development (iOS/Android)'
        : 'Custom RFQ Bidding Marketplace';
      parent_setting_type = 'General Settings';
    } else if (category === 'quote') {
      label_name = 'Data Migration & Retainer Quote';
      parent_setting_type = 'General Settings';
    } else if (category === 'follow_up') {
      label_name = 'Support Ticket Status Follow-Up';
      parent_setting_type = 'General Settings';
    }

    return {
      category,
      label_name,
      parent_setting_type,
      confidence: Math.round(confidence * 100) / 100,
      intent_summary: `Detected intent: ${label_name} (${urgency} urgency)`,
      urgency
    };
  }
}

export const emailClassifier = new EmailClassifier();
