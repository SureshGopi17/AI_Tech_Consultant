"""
Pre-indexed seed articles and screenshots from the Brilliant Directories Solution Center.
Provides high-fidelity, immediate coverage across core functional domains.
"""

from typing import List
from app.models import Article, ArticleImage

SEED_ARTICLES: List[Article] = [
    Article(
        id="art-stripe-billing",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558350-stripe-payment-gateway-setup",
        title="How to Connect Stripe Payment Gateway & Enable Recurring Billing",
        category="Finance & Billing",
        folder="Payment Gateways",
        content="""To connect Stripe to your Brilliant Directories website:
1. Navigate to Settings > General Settings > Payments tab in the Admin Dashboard.
2. Select Stripe as your default Payment Gateway.
3. Enter your Stripe Publishable Key and Stripe Secret Key obtained from your Stripe Dashboard (Developers > API Keys).
4. For live transactions, ensure the Mode dropdown is set to 'Live' rather than 'Test Sandbox'.
5. Enable 'Require CVV Code' and 'Enable 3D Secure / SCA' for European and international compliance.
6. Recurring Billing: Brilliant Directories communicates with Stripe Billing to create recurring subscriptions automatically whenever a member signs up for a paid plan.
7. Webhook Configuration: Copy the Webhook URL from BD Settings > Payments and paste it into Stripe Dashboard > Developers > Webhooks, selecting events: invoice.payment_succeeded, customer.subscription.deleted, and invoice.payment_failed.""",
        summary="Guide on connecting Stripe payment gateway API keys, enabling live mode, and configuring webhooks for automatic recurring billing in Brilliant Directories.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/stripe-settings-admin-panel.png",
                caption="Admin Dashboard > Settings > Payments tab showing Stripe API keys and Webhook URL",
                alt_text="Stripe Payment Gateway Configuration Fields",
                section="Finance & Billing",
                visual_tags=["admin", "settings", "stripe", "billing", "api-keys"]
            ),
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/stripe-webhook-events.png",
                caption="Stripe webhook event selection screen for recurring billing renewals",
                alt_text="Stripe Webhook Events Configuration",
                section="Finance & Billing",
                visual_tags=["stripe", "webhook", "billing"]
            )
        ],
        lastmod="2026-10-01T00:00:00Z",
        hash="hash_stripe_001"
    ),
    Article(
        id="art-search-radius",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558355-change-search-radius-miles-kilometers",
        title="Changing Search Distance Radius from Miles to Kilometers",
        category="Search Settings",
        folder="Location Search",
        content="""To change the distance radius measurement across your directory:
1. Navigate to Settings > General Settings in the Admin Dashboard.
2. Click on the Localization tab.
3. Locate the 'Distance Metric' setting.
4. Switch the option from 'Miles (mi)' to 'Kilometers (km)'.
5. In the same tab, you can set the Default Search Radius (e.g., 25 km, 50 km, or 100 km).
6. Click 'Save Changes' at the bottom of the page.
All front-end search bars, location dropdowns, and Google Maps boundary calculations will immediately update to kilometers without modifying any code.""",
        summary="How to switch the directory distance measurement from miles to kilometers in Settings > Localization.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/localization-distance-metric.png",
                caption="Settings > General Settings > Localization tab showing Distance Metric (Miles vs Kilometers)",
                alt_text="Localization Distance Metric Toggle",
                section="Search Settings",
                visual_tags=["admin", "settings", "search", "localization", "metric"]
            )
        ],
        lastmod="2026-10-01T00:00:00Z",
        hash="hash_search_radius_002"
    ),
    Article(
        id="art-custom-fields-signup",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558360-add-custom-fields-to-member-forms",
        title="How to Add Custom Fields to Member Registration and Profile Forms",
        category="Member Management",
        folder="Form Manager",
        content="""Brilliant Directories allows administrators to add custom input fields to member registration forms without custom coding:
1. Navigate to Toolbox > Form Manager.
2. Locate the 'Listing - Contact Details' or 'Member Sign Up' form and click 'Customize'.
3. Click the '+ Add Field' button on the left sidebar.
4. Choose the Field Type: Single-Line Text, Dropdown Select, Checkboxes, File/Document Upload, or Date Picker.
5. Set the Database Field Name (variable name, e.g., 'license_number' or 'certification_id').
6. Enter the Field Label (the text displayed to members on the front end).
7. Toggle 'Required Field' to ON if members must fill it before completing registration.
8. Set the Visibility: Public (visible on profile) or Admin Only (internal review).
9. Click 'Save Form Changes'. The new field will immediately render on the registration page.""",
        summary="Use Toolbox > Form Manager to add text, file upload, or dropdown fields to member registration without writing code.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/form-manager-add-field.png",
                caption="Toolbox > Form Manager showing Add Field sidebar and field type selector",
                alt_text="Form Manager Add Field Interface",
                section="Member Management",
                visual_tags=["admin", "toolbox", "form-manager", "custom-fields", "signup"]
            )
        ],
        lastmod="2026-10-02T00:00:00Z",
        hash="hash_custom_fields_003"
    ),
    Article(
        id="art-lead-distribution",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558365-auto-lead-distribution-settings",
        title="Auto Lead Distribution & Lead Matching Rules",
        category="Leads & Inquiries",
        folder="Lead Management",
        content="""The Lead Generation system in Brilliant Directories automatically captures visitor inquiries and distributes them to appropriate members:
1. Go to Leads > Lead Settings in the Admin Dashboard.
2. Auto-Match Criteria: You can match leads by Top Category, Sub Category, and Location Radius (Postal Code, City, or State).
3. Max Recipients: Define how many matching members receive each lead (e.g., 1 member for exclusive leads, or top 3-5 members for competitive quotes).
4. Match Priority: Set whether Higher-Tier / Premium Membership plans receive leads before lower-tier members.
5. Monetization: You can provide free leads or require members to pay a set fee (e.g., $15) to accept and unlock the customer's contact details.
6. Email Notification Templates: Customize the 'New Lead Alert' email sent to members in Settings > Email Templates.""",
        summary="Configure Leads > Lead Settings to automatically route inquiries by category and radius, prioritize premium members, or charge per lead.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/lead-distribution-matching.png",
                caption="Leads > Lead Settings showing category matching, radius filter, and max recipient limits",
                alt_text="Lead Auto-Distribution Configuration",
                section="Leads & Inquiries",
                visual_tags=["admin", "leads", "lead-settings", "auto-routing"]
            )
        ],
        lastmod="2026-10-03T00:00:00Z",
        hash="hash_leads_004"
    ),
    Article(
        id="art-category-csv-import",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558401-how-to-import-categories-via-csv-file",
        title="How to Import Member Categories and Sub-Categories via CSV File",
        category="Members & Content",
        folder="Category Management",
        content="""To bulk import your entire category tree from a spreadsheet:
1. Navigate to My Members > Member Categories in the Admin Dashboard.
2. Click the 'Import Categories' button in the upper right corner.
3. Download the sample CSV template to ensure correct column headers:
   - 'Top Category' (Level 1)
   - 'Sub Category' (Level 2)
   - 'Sub-Sub Category' (Level 3)
4. Populate your spreadsheet and save it as a standard UTF-8 encoded .CSV file.
5. In BD, click 'Choose File', select your CSV, and click 'Import Categories'.
6. Duplicate Prevention: Brilliant Directories automatically checks for matching category names to avoid creating duplicate branches.
7. Depth: Brilliant Directories supports up to 3 tiers of category hierarchy out of the box.""",
        summary="Bulk import 3-tier category structures (Top, Sub, Sub-Sub) via My Members > Member Categories using CSV template.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/import-categories-csv-button.png",
                caption="My Members > Member Categories screen showing Import Categories button and CSV upload modal",
                alt_text="Category CSV Import Screen",
                section="Members & Content",
                visual_tags=["admin", "categories", "csv", "import", "hierarchy"]
            )
        ],
        lastmod="2026-10-04T00:00:00Z",
        hash="hash_csv_categories_005"
    ),
    Article(
        id="art-member-csv-import",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558405-bulk-import-members-via-csv",
        title="How to Bulk Import 500+ Members from a CSV Spreadsheet",
        category="Member Management",
        folder="Import Members",
        content="""To bulk import member records from an Excel/CSV spreadsheet:
1. Navigate to My Members > Import Members.
2. Download the default Member Import CSV Template to see all accepted fields (first_name, last_name, company, email, phone, address, city, state, zip, country, top_category, sub_category, membership_plan_id).
3. Duplicate Handling: Under 'Import Options', select 'Skip Existing Records' or 'Update Existing Records Based on Email Address'.
4. Automatic Geocoding: Check the box 'Automatically Geocode Address Coordinates'. Brilliant Directories will fetch Latitude & Longitude for map pins.
5. Upload your CSV and click 'Review Field Mapping'. Confirm your CSV headers match BD database columns.
6. Click 'Process Import'. The batch processor will import records in batches of 50-100 to ensure server stability. You can import thousands of members smoothly.""",
        summary="Use My Members > Import Members to bulk import member records from CSV with automatic address geocoding and duplicate email checks.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/member-csv-import-mapper.png",
                caption="Column mapping interface for importing member records from CSV",
                alt_text="Member CSV Field Mapping Interface",
                section="Member Management",
                visual_tags=["admin", "members", "import", "csv", "mapping"]
            )
        ],
        lastmod="2026-10-04T00:00:00Z",
        hash="hash_member_import_006"
    ),
    Article(
        id="art-google-tag-manager",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558410-connect-google-tag-manager-ga4",
        title="Connecting Google Tag Manager (GTM) and Google Analytics 4 (GA4)",
        category="Integrations & Analytics",
        folder="Tracking & Scripts",
        content="""To install Google Tag Manager or Google Analytics 4 tracking scripts:
1. Navigate to Settings > General Settings > Integrations tab.
2. In the 'Google Analytics 4 Measurement ID' field, enter your G-XXXXXXXXXX ID.
3. For Google Tag Manager:
   - In Settings > Design Settings > Custom CSS / HEAD tab, paste the GTM container <script> code inside the 'Head Code' box.
   - Paste the <noscript> GTM snippet into the 'Body Code' box.
4. Click 'Save Changes'.
The GTM container and GA4 tracking will fire automatically across all public pages, search results, member listings, and checkout pages.""",
        summary="Insert GTM container code into Settings > Design Settings > Custom CSS/HEAD or GA4 ID into Settings > Integrations.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/design-settings-head-code.png",
                caption="Settings > Design Settings > Custom CSS/HEAD tab showing Head Code and Body Code input boxes",
                alt_text="Custom Head and Body Code Input Settings",
                section="Integrations & Analytics",
                visual_tags=["admin", "settings", "gtm", "analytics", "tracking", "code"]
            )
        ],
        lastmod="2026-10-05T00:00:00Z",
        hash="hash_gtm_007"
    ),
    Article(
        id="art-review-moderation",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558415-member-review-moderation-settings",
        title="Enabling Member Review Moderation Before Publishing",
        category="Community & Content",
        folder="Member Reviews",
        content="""To ensure client reviews do not appear on member profiles without prior admin approval:
1. Go to Content > Member Reviews in the Admin Dashboard.
2. Click on the 'Review Settings' button at the top.
3. Set the 'Review Moderation' toggle to 'Require Admin Approval'.
4. Optional: Enable 'Allow Members to Reply to Reviews' so profile owners can post public rebuttals or thank-you messages.
5. In the Member Reviews table, all incoming reviews will enter the 'Pending' tab. Administrators can read the rating, review comments, and click 'Approve' or 'Reject'.""",
        summary="Set Content > Member Reviews > Review Settings to 'Require Admin Approval' to hold all reviews in moderation queue.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/review-moderation-toggle.png",
                caption="Content > Member Reviews > Review Settings showing Require Admin Approval toggle",
                alt_text="Review Moderation Settings Interface",
                section="Community & Content",
                visual_tags=["admin", "reviews", "moderation", "settings"]
            )
        ],
        lastmod="2026-10-05T00:00:00Z",
        hash="hash_reviews_008"
    ),
    Article(
        id="art-email-templates",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558420-custom-email-templates-welcome-sequence",
        title="Customizing Automated Welcome Emails & Notification Templates",
        category="Emails & Notifications",
        folder="Email Templates",
        content="""Brilliant Directories includes over 50 pre-designed system email templates:
1. Navigate to Emails > Email Templates in the Admin Dashboard.
2. Locate the 'Welcome Email - Paid Member' or 'Welcome Email - Free Member' template.
3. Click 'Customize'.
4. Use the WYSIWYG rich text editor to edit email copy, colors, and headers.
5. Available Dynamic Merge Tags:
   - %first_name% : Member's first name
   - %last_name% : Member's last name
   - %user_email% : Member login email
   - %membership_plan% : Plan name
   - %login_url% : Direct link to member login
6. Click 'Save Template' and use the 'Send Test Email' button to verify delivery.""",
        summary="Edit automated welcome and notification emails in Emails > Email Templates using merge tags like %first_name% and %login_url%.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/email-template-editor.png",
                caption="Emails > Email Templates showing WYSIWYG editor and available variable merge tags",
                alt_text="Email Template WYSIWYG Editor",
                section="Emails & Notifications",
                visual_tags=["admin", "emails", "templates", "merge-tags"]
            )
        ],
        lastmod="2026-10-06T00:00:00Z",
        hash="hash_emails_009"
    ),
    Article(
        id="art-claim-listing",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558425-claim-listing-feature-setup",
        title="How Members Claim Existing Listings and Upgrade to Paid Plans",
        category="Member Management",
        folder="Claim Listings",
        content="""The 'Claim This Listing' feature allows directory owners to pre-populate thousands of unclaimed profiles to drive monetization:
1. Navigate to My Members > Membership Plans.
2. Edit or create your 'Unclaimed / Basic' plan.
3. Under the 'Profile Page Settings' tab, toggle 'Enable Claim Listing Button' to ON.
4. Set the Claiming Redirect: Choose whether claiming directs the user to a free verification form or straight to a Paid Plan checkout page (e.g. $49/mo).
5. On the public listing page, an eye-catching 'Claim This Listing' badge appears.
6. When clicked, the business owner enters their email, confirms verification, selects their desired paid plan, completes checkout, and immediately gains admin control of the profile.""",
        summary="Enable 'Claim This Listing' button in Membership Plans > Profile Page Settings to let business owners claim profiles and upgrade.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/claim-listing-profile-badge.png",
                caption="Public member profile displaying the 'Claim This Listing' button and upgrade banner",
                alt_text="Claim Listing Button on Public Profile",
                section="Member Management",
                visual_tags=["claim-listing", "profile", "membership-plan", "monetization"]
            )
        ],
        lastmod="2026-10-06T00:00:00Z",
        hash="hash_claim_010"
    ),
    Article(
        id="art-private-directory-permissions",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558430-restrict-search-logged-in-members-only",
        title="Restricting Member Directory and Search Results to Logged-In Users",
        category="Privacy & Security",
        folder="Access Control",
        content="""To make your directory private so only registered or paying members can search and view profiles:
1. Navigate to Settings > General Settings > Privacy tab.
2. Enable 'Require Login to View Member Profiles' or 'Require Login to View Search Results'.
3. Set the 'Restricted Access Redirect' option to your Member Login or Signup landing page.
4. Granular Membership Permissions: You can also configure visibility per Membership Plan. Under My Members > Membership Plans > Search Results tab, toggle whether this plan's contact info (phone number, website link, email) is public or visible only to logged-in users.""",
        summary="Make search results or contact details private in Settings > General Settings > Privacy tab or via Membership Plan permissions.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/privacy-settings-require-login.png",
                caption="Settings > General Settings > Privacy tab showing Require Login toggles",
                alt_text="Privacy and Access Control Settings",
                section="Privacy & Security",
                visual_tags=["admin", "privacy", "security", "permissions", "login"]
            )
        ],
        lastmod="2026-10-07T00:00:00Z",
        hash="hash_privacy_011"
    ),
    Article(
        id="art-webhooks-zapier",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558435-webhooks-api-integrations-zapier",
        title="Configuring Outbound Webhooks and Zapier / CRM Integrations",
        category="Integrations & API",
        folder="Webhooks",
        content="""Brilliant Directories supports outbound webhooks to sync events into Zapier, Make, HubSpot, or custom APIs:
1. Navigate to Settings > Webhooks in the Admin Dashboard.
2. Click '+ Add Webhook'.
3. Select the Trigger Event:
   - 'Member Signup'
   - 'Member Upgraded Plan'
   - 'Member Cancelled / Deleted'
   - 'New Lead Received'
   - 'New Review Submitted'
4. Enter your destination Webhook Endpoint URL (e.g. from Zapier Catch Webhook or your internal CRM endpoint).
5. Payload Format: BD sends JSON formatted payloads containing full member details (ID, name, email, plan, custom fields, timestamp).
6. Click 'Send Test Payload' to verify connection and save.""",
        summary="Set up outbound webhooks in Settings > Webhooks for Member Signup, Upgrades, Leads, and Reviews to sync with CRMs.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/webhooks-admin-manager.png",
                caption="Settings > Webhooks screen with Trigger Event dropdown and webhook URL field",
                alt_text="Webhooks Manager Interface",
                section="Integrations & API",
                visual_tags=["admin", "webhooks", "api", "crm", "zapier"]
            )
        ],
        lastmod="2026-10-07T00:00:00Z",
        hash="hash_webhooks_012"
    ),
    Article(
        id="art-discount-coupons",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558440-create-discount-coupon-codes",
        title="How to Create Promo Discount Coupon Codes in the Finance Section",
        category="Finance & Billing",
        folder="Promo Codes",
        content="""To create discount promo codes for memberships or digital products:
1. Navigate to Finance > Promo Codes in the Admin Dashboard.
2. Click 'New Promo Code'.
3. Enter the Code Name (e.g., 'BLACKFRIDAY20' or 'SUMMER50').
4. Select Discount Type:
   - 'Percentage Off' (e.g., 20%)
   - 'Fixed Dollar Amount' (e.g., $50 off)
5. Select Applicable Membership Plans: Apply to all plans or specific paid tiers.
6. Recurring Discount: Choose whether discount applies only to the initial payment or to all recurring monthly/annual renewal billing cycles.
7. Expiration Date & Usage Limit: Set optional expiration timestamp or max redemptions (e.g., first 100 signups).
8. Click 'Save Promo Code'.""",
        summary="Create percentage or fixed dollar discount codes in Finance > Promo Codes with optional recurring renewal application.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/promo-codes-new-modal.png",
                caption="Finance > Promo Codes creation modal with discount type and recurring toggle",
                alt_text="Promo Code Creation Interface",
                section="Finance & Billing",
                visual_tags=["admin", "finance", "coupons", "promo-codes", "billing"]
            )
        ],
        lastmod="2026-10-08T00:00:00Z",
        hash="hash_coupons_013"
    ),
    Article(
        id="art-video-reels-profiles",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558445-embed-video-reels-youtube-vimeo",
        title="Enabling Video Reels and YouTube/Vimeo Embeds on Member Profiles",
        category="Member Management",
        folder="Profile Features",
        content="""To allow members to showcase video portfolios and showreels on their profile pages:
1. Navigate to My Members > Membership Plans.
2. Click 'Edit' on the desired membership tier.
3. Open the 'Post Publishing' or 'Profile Page Features' tab.
4. Locate the 'Video Embeds / YouTube & Vimeo' feature toggle and set it to 'Enabled'.
5. Set Max Allowed Videos (e.g. 1 video for Basic, up to 10 for Premium).
6. On the member's profile edit dashboard, a 'Manage Videos' tab will appear where they paste YouTube or Vimeo video URLs.
7. The videos render in an interactive responsive video carousel on the member's public profile page.""",
        summary="Enable video embeds in My Members > Membership Plans > Post Publishing to let members display YouTube and Vimeo videos.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/membership-plan-video-toggle.png",
                caption="Membership Plan settings showing Video Embeds toggle and maximum video count",
                alt_text="Video Embeds Setting in Membership Plan",
                section="Member Management",
                visual_tags=["admin", "membership-plan", "video", "profile"]
            )
        ],
        lastmod="2026-10-08T00:00:00Z",
        hash="hash_video_014"
    ),
    Article(
        id="art-cancellation-refund-policy",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558450-handling-member-cancellations-refunds",
        title="How Member Cancellations, Prorated Credits, and Refunds are Handled",
        category="Finance & Billing",
        folder="Cancellations & Refunds",
        content="""How cancellations and refunds operate in Brilliant Directories:
1. Member Self-Cancellation:
   - Members can cancel their recurring subscription from their account settings if 'Allow Self-Service Cancellation' is enabled in Settings > General Settings > Payments.
   - When a member cancels, their subscription in Stripe is set to cancel at period end (they retain access until the end of the paid billing cycle).
2. Admin Manual Cancellation:
   - Navigate to My Members > Search Members, locate member, click 'Actions' > 'Cancel Subscription'.
3. Issuing Refunds:
   - In Finance > Transaction History, search for the Invoice ID or Member Email.
   - Click 'Actions' > 'Issue Full Refund' or 'Issue Partial Refund'.
   - BD immediately instructs Stripe via API to refund the charge back to the customer's credit card.
   - An automated refund receipt email is sent to the customer.""",
        summary="Manage member cancellations via My Members or self-service, and issue full or partial Stripe refunds in Finance > Transaction History.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/finance-issue-refund.png",
                caption="Finance > Transaction History showing Issue Full Refund and Issue Partial Refund action modal",
                alt_text="Refund Action Modal in Finance",
                section="Finance & Billing",
                visual_tags=["admin", "finance", "refunds", "cancellations", "transactions"]
            )
        ],
        lastmod="2026-10-09T00:00:00Z",
        hash="hash_refund_015"
    ),
    Article(
        id="art-theme-custom-css",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558455-design-settings-brand-colors-custom-css",
        title="Customizing Theme Colors, Typography, and Adding Custom CSS",
        category="Design & Branding",
        folder="Theme Settings",
        content="""To tailor directory aesthetics to client brand guidelines:
1. Navigate to Settings > Design Settings in the Admin Dashboard.
2. Colors & Styling: Use the visual color pickers for Primary Brand Color, Secondary Accent, Header Background, and Navigation Links.
3. Typography: Select heading and body fonts from Google Fonts integration (e.g. Montserrat, Playfair Display, Inter, Roboto).
4. Custom CSS Injection:
   - Go to Settings > Design Settings > Custom CSS / HEAD tab.
   - Enter custom CSS classes into the 'Additional CSS Styles' box.
   - These styles take precedence over default Bootstrap styling.
5. Live Preview: Changes can be previewed instantly before saving.""",
        summary="Customize brand colors, typography, and custom CSS in Settings > Design Settings without editing core template files.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/design-settings-colors.png",
                caption="Settings > Design Settings showing primary color pickers and typography selectors",
                alt_text="Design Settings Color and Typography Interface",
                section="Design & Branding",
                visual_tags=["admin", "design", "colors", "css", "theme"]
            )
        ],
        lastmod="2026-10-09T00:00:00Z",
        hash="hash_design_016"
    ),
    Article(
        id="art-google-maps-api",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558460-google-maps-api-key-configuration",
        title="Configuring Google Maps API Key & Fixing Location Pin Issues",
        category="Integrations & API",
        folder="Google Maps",
        content="""Brilliant Directories requires a valid Google Maps API Key with geocoding permissions:
1. Navigate to Settings > General Settings > Integrations tab.
2. Locate the 'Google Maps API Key' field and paste your API key.
3. Required Google Cloud APIs to enable in your Google Cloud Console:
   - Maps JavaScript API
   - Geocoding API
   - Places API
4. Common issues: If map pins are missing or geocoding fails, verify that:
   - Billing is active on your Google Cloud account.
   - HTTP referrers restriction in Google Cloud Console includes: 'https://*.yourdomain.com/*'.
   - Geocoding API quota has not been exceeded.""",
        summary="Set up Google Maps API Key in Settings > Integrations and ensure Geocoding and Places APIs are enabled in Google Cloud Console.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/google-maps-api-settings.png",
                caption="Settings > General Settings > Integrations showing Google Maps API Key input",
                alt_text="Google Maps API Key Setting Field",
                section="Integrations & API",
                visual_tags=["admin", "google-maps", "api-key", "geocoding", "location"]
            )
        ],
        lastmod="2026-10-10T00:00:00Z",
        hash="hash_maps_017"
    ),
    Article(
        id="art-custom-domain-ssl",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558465-connecting-custom-domain-ssl-setup",
        title="Connecting a Custom Domain Name and Free SSL Certificate",
        category="Domain & Hosting",
        folder="Domain Settings",
        content="""To connect your own domain (e.g. www.yourdirectory.com) to Brilliant Directories:
1. Navigate to Settings > Domain Settings in your BD Admin Panel.
2. In your domain registrar (GoDaddy, Namecheap, Cloudflare), set up the following DNS records:
   - Type A Record: Host '@' pointing to BD server IP (found in Domain Settings).
   - Type CNAME Record: Host 'www' pointing to your directory subdomain.
3. Return to BD Domain Settings and click 'Validate DNS Records'.
4. Free SSL Certificate: Once DNS propagates, click 'Install Free SSL Certificate'.
5. Brilliant Directories automatically generates and installs a Let's Encrypt SSL certificate and enforces HTTPS across all pages.""",
        summary="Point A and CNAME records to Brilliant Directories IP in your DNS registrar, then click 'Install Free SSL Certificate'.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/domain-settings-dns-validator.png",
                caption="Settings > Domain Settings showing DNS IP records and SSL activation status",
                alt_text="Domain Settings and DNS Validator Screen",
                section="Domain & Hosting",
                visual_tags=["admin", "domain", "dns", "ssl", "hosting"]
            )
        ],
        lastmod="2026-10-10T00:00:00Z",
        hash="hash_domain_018"
    ),
    Article(
        id="art-platform-overview",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558500-how-the-product-works-platform-overview",
        title="Overview: How Brilliant Directories Platform and Product Works",
        category="Platform Architecture & Features",
        folder="Getting Started",
        content="""Brilliant Directories is a complete all-in-one SaaS platform for launching, managing, and monetizing searchable directory and marketplace websites.

Here is how the product works across its core functional modules:
1. Member Management Engine: Manage professional profiles, business listings, and tiered membership plans with self-service member portals.
2. Search & Geolocation Engine: Visitors and members can search by keyword, business categories, location radius (in miles or kilometers), and custom filter fields.
3. Monetization & Stripe Billing: Connect Stripe to collect setup fees and automatic recurring monthly/annual subscription renewals, with automated dunning and promo discount coupons.
4. Automated Lead Distribution: Visitors submit project inquiries or quote requests, which the system automatically routes to matched members based on location and specialty.
5. Content & Reviews Engine: Built-in community features including member review moderation, classifieds, digital events, and blog post publishing.
6. Integrations & Developer Webhooks: Native webhooks connect to Zapier and external CRMs, with custom JavaScript header injection for Google Tag Manager and analytics.

All settings and workflows are managed without writing code through the web-based Admin Dashboard.""",
        summary="Comprehensive overview of how the Brilliant Directories platform and product works across member management, search, Stripe monetization, and lead distribution.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/admin-dashboard-overview.png",
                caption="Brilliant Directories Admin Dashboard Overview showing member search, revenue, and content modules",
                alt_text="Brilliant Directories Dashboard Overview",
                section="Getting Started",
                visual_tags=["admin", "dashboard", "overview", "product", "platform"]
            )
        ],
        lastmod="2026-10-15T00:00:00Z",
        hash="hash_overview_019"
    ),
    Article(
        id="art-sitemap-management-verification",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558600-add-sitemaps-and-verify-urls-knowledge-brain",
        title="How to Add Sitemaps, Verify Discovered URLs, and Monitor Ingestion in Knowledge Brain",
        category="Knowledge Base Management",
        folder="Sitemap Ingestion",
        content="""To add custom sitemaps and verify URLs in your Knowledge Brain dashboard:
1. Navigate to the Knowledge Base Dashboards panel in the Knowledge Brain UI.
2. Under 'Custom Sitemap Management', enter one or multiple sitemap URLs (e.g., https://support.brilliantdirectories.com/support/solutions/sitemap.xml).
3. Pre-Flight Inspection: Click 'Inspect & Analyze Sitemaps'. The system inspects child sitemaps and calculates:
   - Grand Total Discovered URLs
   - Ingestion Speed: 240 pages/hour (5,760 pages/day)
   - Estimated Completion Time (ETA)
4. User Confirmation Gate: A modal opens showing the breakdown. Click 'Confirm & Begin Ingestion' to approve crawling.
5. URL Discovery & Verification:
   - Click 'Verify Discovered URLs' to audit all indexed URLs with checking time in milliseconds.
   - Filter by All, Active (200 OK), Quarantined, Missing, or Pending.
   - Inspect individual URLs, metadata, summaries, HTTP codes, and screenshot counts.
6. URL Count Reconciliation Report:
   - Compare Discovered, Processed, Successfully Indexed, Skipped, and Failed URLs.
   - Guaranteed Invariant: No URL is ever marked as successfully indexed unless its indexing operation actually succeeded.""",
        summary="Complete guide to adding single or multiple sitemaps, running pre-flight inspection with speed benchmarks, confirming ingest, and verifying URLs with reconciliation reports.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/sitemap-preflight-modal.png",
                caption="Pre-Flight Sitemap Inspection showing child sitemaps, 240 pgs/hr speed, and user confirmation gate",
                alt_text="Sitemap Preflight Modal",
                section="Knowledge Base Management",
                visual_tags=["sitemap", "urls", "verification", "preflight", "ingest"]
            )
        ],
        lastmod="2026-10-23T00:00:00Z",
        hash="hash_sitemap_020"
    ),
    Article(
        id="art-missing-urls-and-jwt-auth",
        url="https://support.brilliantdirectories.com/support/solutions/articles/5000558610-missing-urls-retention-and-jwt-auth-security",
        title="Handling Missing URLs (Never-Deleted Retention) and Secure JWT Authentication",
        category="Security & Retention Architecture",
        folder="System Architecture",
        content="""Knowledge Brain features an enterprise retention architecture and cryptographic JWT security:
1. Secure JWT Authentication:
   - All user sessions, logins, registrations, and demo logins are secured with cryptographically signed JSON Web Tokens (JWT) using the HS256 algorithm.
   - Standard claims include subject (sub), user email, full name, role, active dashboard ID, issued-at (iat), and expiration (exp) valid for 24 hours.
   - JWT tokens are automatically stored in browser localStorage and sent via 'Authorization: Bearer <token>' on all API requests.
2. Missing URLs & Multi-Level Quarantine:
   - When a URL returns HTTP 404 or is removed from the sitemap, it is flagged and quarantined after X consecutive refresh checks (configurable threshold X, default 3).
   - 301 redirects are quarantined and their canonical destination URLs are followed and indexed.
   - If a URL recovers (returns 200 OK), its consecutive failure count automatically resets to 0.
3. Archived Retention Store (Never Deleted Invariant):
   - Missing or deprecated URLs are NEVER permanently deleted from the database.
   - They are archived in data/archived_store.json with timestamp, consecutive misses, and reason.
   - Configurable retention periods: Archive immediately, after 2 checks, 15 checks, or 30 checks.
   - 1-Click Restore: Administrators can restore archived URLs back into the active index at any time with a single click.""",
        summary="Overview of JWT authentication (HS256 Bearer tokens), multi-level quarantine for 404/301 URLs, and the never-deleted archived retention store with 1-click restore.",
        images=[
            ArticleImage(
                url="https://support.brilliantdirectories.com/images/archived-urls-restore-panel.png",
                caption="Archived URLs repository showing never-deleted status and 1-click restore button",
                alt_text="Archived URLs Retention Panel",
                section="Security & Retention Architecture",
                visual_tags=["archive", "jwt", "auth", "retention", "quarantine", "restore"]
            )
        ],
        lastmod="2026-10-23T00:00:00Z",
        hash="hash_jwt_arch_021"
    )
]
