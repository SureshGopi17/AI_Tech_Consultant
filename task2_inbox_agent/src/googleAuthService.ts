/**
 * Google OAuth 2.0 Authentication Service for Task 2: The Inbox Agent.
 * Handles:
 * - Official Google OAuth 2.0 flow
 * - Generating authorization URLs with secure scopes
 * - Exchanging authorization codes for tokens
 * - Token refresh and secure server-side persistence
 * - User profile retrieval (email, name, picture)
 * - Safe disconnect and multi-account switching
 */

import { google } from 'googleapis';
import * as fs from 'fs';
import * as path from 'path';
import { GoogleAuthStatus, GoogleUserProfile, GmailConfig } from './types';

const DATA_DIR = path.join(__dirname, '..', 'data');
const TOKENS_PATH = path.join(DATA_DIR, 'google_tokens.json');
const CONFIG_PATH = path.join(DATA_DIR, 'gmail_config.json');

export const GMAIL_SCOPES = [
  'https://www.googleapis.com/auth/userinfo.email',
  'https://www.googleapis.com/auth/userinfo.profile',
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.compose',
  'https://www.googleapis.com/auth/gmail.readonly'
];

export class GoogleAuthService {
  private oauth2Client: any = null;
  private tokens: any = null;

  constructor() {
    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }
    this.loadTokens();
    this.initOAuthClient();
  }

  private getCredentials(): { clientId: string; clientSecret: string; redirectUri: string } {
    let clientId = process.env.GOOGLE_CLIENT_ID || '';
    let clientSecret = process.env.GOOGLE_CLIENT_SECRET || '';
    let redirectUri = process.env.GOOGLE_REDIRECT_URI || 'http://localhost:8002/api/v1/auth/google/callback';

    // Check saved config in data/gmail_config.json as well
    if (fs.existsSync(CONFIG_PATH)) {
      try {
        const config: GmailConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
        if (config.client_id) clientId = config.client_id;
        if (config.client_secret) clientSecret = config.client_secret;
        if (config.redirect_uri) redirectUri = config.redirect_uri;
      } catch (err) {
        // ignore
      }
    }

    return { clientId, clientSecret, redirectUri };
  }

  public initOAuthClient() {
    const { clientId, clientSecret, redirectUri } = this.getCredentials();
    if (clientId && clientSecret) {
      this.oauth2Client = new google.auth.OAuth2(clientId, clientSecret, redirectUri);
      if (this.tokens) {
        this.oauth2Client.setCredentials(this.tokens);
      }
    } else {
      this.oauth2Client = null;
    }
  }

  private loadTokens() {
    if (fs.existsSync(TOKENS_PATH)) {
      try {
        const raw = fs.readFileSync(TOKENS_PATH, 'utf-8');
        this.tokens = JSON.parse(raw);
      } catch (err) {
        console.error('[GoogleAuthService] Error reading tokens file:', err);
        this.tokens = null;
      }
    }
  }

  private saveTokens(tokens: any) {
    this.tokens = tokens;
    fs.writeFileSync(TOKENS_PATH, JSON.stringify(tokens, null, 2), 'utf-8');
    if (this.oauth2Client) {
      this.oauth2Client.setCredentials(tokens);
    }
  }

  /**
   * Generates official Google OAuth 2.0 authorization URL
   */
  public getAuthUrl(customRedirectUri?: string): { url: string; has_credentials: boolean; scopes: string[]; message?: string } {
    const { clientId, clientSecret, redirectUri } = this.getCredentials();
    const targetRedirect = customRedirectUri || redirectUri;

    if (!clientId || !clientSecret) {
      return {
        url: '',
        has_credentials: false,
        scopes: GMAIL_SCOPES,
        message: 'Google OAuth Client ID & Client Secret are not configured yet. Configure them in Settings or .env.'
      };
    }

    const client = new google.auth.OAuth2(clientId, clientSecret, targetRedirect);
    const url = client.generateAuthUrl({
      access_type: 'offline',
      prompt: 'consent',
      scope: GMAIL_SCOPES
    });

    return {
      url,
      has_credentials: true,
      scopes: GMAIL_SCOPES
    };
  }

  /**
   * Handles OAuth callback: exchanges authorization code for tokens and retrieves user profile
   */
  public async handleCallback(code: string, customRedirectUri?: string): Promise<GoogleUserProfile> {
    const { clientId, clientSecret, redirectUri } = this.getCredentials();
    const targetRedirect = customRedirectUri || redirectUri;

    if (!clientId || !clientSecret) {
      throw new Error('Google OAuth credentials not configured on the server.');
    }

    const client = new google.auth.OAuth2(clientId, clientSecret, targetRedirect);
    const { tokens } = await client.getToken(code);
    client.setCredentials(tokens);
    this.saveTokens(tokens);
    this.oauth2Client = client;

    // Fetch user profile from Google OAuth2 API
    const oauth2 = google.oauth2({ version: 'v2', auth: client });
    const { data } = await oauth2.userinfo.get();

    const profile: GoogleUserProfile = {
      id: data.id || undefined,
      email: data.email || 'connected-user@gmail.com',
      name: data.name || data.email?.split('@')[0] || 'Google User',
      given_name: data.given_name || undefined,
      family_name: data.family_name || undefined,
      picture: data.picture || undefined,
      locale: data.locale || undefined,
      verified_email: data.verified_email || true,
      connected_at: new Date().toISOString()
    };

    // Update config store
    this.updateConnectedProfile(profile);

    return profile;
  }

  /**
   * Connects in Demo Sandbox mode (e.g. for evaluators without their own Google Cloud console setup)
   */
  public connectDemoUser(customEmail?: string, customName?: string): GoogleUserProfile {
    const email = customEmail || 'consultant.demo@gmail.com';
    const name = customName || 'Suresh Gopi';

    const profile: GoogleUserProfile = {
      id: 'demo-google-user-01',
      email,
      name,
      given_name: name.split(' ')[0],
      family_name: name.split(' ')[1] || 'Consultant',
      picture: 'https://lh3.googleusercontent.com/a/default-user',
      verified_email: true,
      connected_at: new Date().toISOString()
    };

    // Set demo token
    const demoTokens = {
      access_type: 'demo',
      connected_at: profile.connected_at
    };
    this.saveTokens(demoTokens);
    this.updateConnectedProfile(profile, 'demo');

    return profile;
  }

  private updateConnectedProfile(profile: GoogleUserProfile, mode: 'live' | 'demo' = 'live') {
    let config: GmailConfig = {
      mode,
      gmail_address: profile.email,
      auth_type: 'oauth',
      imap_host: 'imap.gmail.com:993',
      smtp_host: 'smtp.gmail.com:587',
      is_connected: true,
      last_sync: new Date().toISOString(),
      user_profile: profile
    };

    if (fs.existsSync(CONFIG_PATH)) {
      try {
        const existing = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
        config = {
          ...existing,
          mode,
          gmail_address: profile.email,
          auth_type: 'oauth',
          is_connected: true,
          last_sync: new Date().toISOString(),
          user_profile: profile
        };
      } catch (err) {
        // ignore
      }
    }

    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2), 'utf-8');
  }

  /**
   * Disconnects Google account
   */
  public disconnect(): { success: boolean; message: string } {
    this.tokens = null;
    this.oauth2Client = null;
    if (fs.existsSync(TOKENS_PATH)) {
      try {
        fs.unlinkSync(TOKENS_PATH);
      } catch (err) {
        // ignore
      }
    }

    if (fs.existsSync(CONFIG_PATH)) {
      try {
        const config: GmailConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
        config.is_connected = false;
        config.user_profile = undefined;
        fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2), 'utf-8');
      } catch (err) {
        // ignore
      }
    }

    return {
      success: true,
      message: 'Google account disconnected successfully.'
    };
  }

  /**
   * Returns current authenticated OAuth2Client (ready for googleapis)
   */
  public getAuthenticatedClient(): any {
    if (!this.oauth2Client && this.tokens) {
      this.initOAuthClient();
    }
    return this.oauth2Client;
  }

  /**
   * Returns current connection status and profile details (safe for frontend)
   */
  public getStatus(): GoogleAuthStatus {
    const { clientId } = this.getCredentials();
    let isConnected = false;
    let profile: GoogleUserProfile | undefined;
    let authType: 'oauth2' | 'demo' = 'oauth2';

    if (fs.existsSync(CONFIG_PATH)) {
      try {
        const config: GmailConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
        isConnected = !!config.is_connected;
        profile = config.user_profile;
        if (config.mode === 'demo') {
          authType = 'demo';
        }
      } catch (err) {
        // ignore
      }
    }

    // Default profile if connected in demo
    if (isConnected && !profile) {
      profile = {
        email: 'consultant.demo@gmail.com',
        name: 'Lead AI Consultant',
        picture: 'https://lh3.googleusercontent.com/a/default-user',
        connected_at: new Date().toISOString()
      };
    }

    return {
      is_connected: isConnected,
      user: profile,
      user_profile: profile,
      auth_type: authType,
      has_client_credentials: !!clientId,
      client_id_preview: clientId ? `${clientId.slice(0, 12)}...` : undefined,
      scopes: GMAIL_SCOPES,
      message: isConnected
        ? `Connected to Google account: ${profile?.email}`
        : 'No Google account connected.'
    };
  }

  /**
   * Saves updated OAuth Client credentials
   */
  public saveOAuthCredentials(clientId: string, clientSecret: string, redirectUri?: string): { success: boolean; message: string } {
    let config: any = {};
    if (fs.existsSync(CONFIG_PATH)) {
      try {
        config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
      } catch (err) {
        // ignore
      }
    }

    config.client_id = clientId.trim();
    config.client_secret = clientSecret.trim();
    if (redirectUri) {
      config.redirect_uri = redirectUri.trim();
    }
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2), 'utf-8');

    this.initOAuthClient();

    return {
      success: true,
      message: 'Google OAuth credentials saved successfully.'
    };
  }
}

export const googleAuthService = new GoogleAuthService();
