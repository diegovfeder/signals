/**
 * Signal notification email template for trading alerts
 */

import { buildEmailHTML, EMAIL_THEME } from "./theme";
import type { EmailTemplate } from "./types";
import { TEMPLATE_KEYS } from "./types";

export const signalNotificationTemplate: EmailTemplate = {
  name: TEMPLATE_KEYS.SIGNAL_NOTIFICATION,
  alias: "signal-notification",
  subject: "{{{SYMBOL}}} Signal: {{{SIGNAL_TYPE}}}",
  html: buildSignalNotificationHTML(),
  text: buildSignalNotificationText(),
  variables: [
    { key: "SYMBOL", type: "string", fallbackValue: "ASSET" },
    { key: "SIGNAL_TYPE", type: "string", fallbackValue: "HOLD" },
    { key: "STRENGTH", type: "number", fallbackValue: 0 },
    { key: "PRICE", type: "string", fallbackValue: "0.00" },
    { key: "TIMESTAMP", type: "string", fallbackValue: "now" },
    {
      key: "REASONING_HTML",
      type: "string",
      fallbackValue: "<li>No reasoning provided.</li>",
    },
    {
      key: "REASONING_TEXT",
      type: "string",
      fallbackValue: "- No reasoning provided.",
    },
    {
      key: "EXPLANATION_HTML",
      type: "string",
      fallbackValue: "",
    },
    {
      key: "EXPLANATION_TEXT",
      type: "string",
      fallbackValue: "",
    },
    { key: "UNSUBSCRIBE_URL", type: "string" },
  ],
};

function buildSignalNotificationHTML(): string {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 32px 16px; background: ${EMAIL_THEME.background}; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
  <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto;">
    <tr>
      <td>
        <div style="background: ${EMAIL_THEME.card}; border: 1px solid ${EMAIL_THEME.cardBorder}; border-radius: 24px; padding: 40px; box-shadow: 0 20px 60px rgba(3, 7, 5, 0.55);">
          <p style="margin: 0 0 20px 0; display: inline-block; padding: 6px 12px; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: ${EMAIL_THEME.badgeText}; background: ${EMAIL_THEME.badgeBg}; border-radius: 999px; border: 1px solid ${EMAIL_THEME.divider};">Signal Alert</p>
          <h1 style="margin: 0 0 12px 0; font-size: 28px; color: ${EMAIL_THEME.textPrimary};">New {{{SIGNAL_TYPE}}} signal for {{{SYMBOL}}}</h1>
          <p style="margin: 0 0 18px 0; font-size: 16px; line-height: 1.6; color: ${EMAIL_THEME.textSecondary};">Generated at {{{TIMESTAMP}}}</p>

          <div style="margin: 24px 0; padding: 24px; border-radius: 12px; background: ${EMAIL_THEME.badgeBg}; border: 1px solid ${EMAIL_THEME.divider};">
            <p style="margin: 0 0 16px 0; font-size: 48px; font-weight: bold; color: ${EMAIL_THEME.badgeText}; text-align: center;">{{{SIGNAL_TYPE}}}</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div>
                <p style="margin: 0; font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: ${EMAIL_THEME.muted};">Strength</p>
                <p style="margin: 6px 0 0 0; font-size: 20px; color: ${EMAIL_THEME.textPrimary}; font-weight: 600;">{{{STRENGTH}}} / 100</p>
              </div>
              <div>
                <p style="margin: 0; font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: ${EMAIL_THEME.muted};">Price</p>
                <p style="margin: 6px 0 0 0; font-size: 20px; color: ${EMAIL_THEME.textPrimary}; font-weight: 600;">$\${{{PRICE}}}</p>
              </div>
            </div>
          </div>

          <div style="margin: 24px 0;">
            <p style="margin: 0 0 12px 0; font-size: 15px; letter-spacing: 0.08em; text-transform: uppercase; color: ${EMAIL_THEME.muted};">Key Factors</p>
            <ul style="margin: 0 0 16px 20px; padding: 0; color: ${EMAIL_THEME.textSecondary}; font-size: 15px; line-height: 1.6;">
              {{{REASONING_HTML}}}
            </ul>
          </div>

          {{#EXPLANATION_HTML}}
          <div style="margin: 24px 0; padding: 20px; border-radius: 12px; background: ${EMAIL_THEME.badgeBg}; border-left: 3px solid ${EMAIL_THEME.ring};">
            <p style="margin: 0 0 12px 0; font-size: 15px; letter-spacing: 0.08em; text-transform: uppercase; color: ${EMAIL_THEME.badgeText};">Analysis</p>
            <div style="margin: 0; color: ${EMAIL_THEME.textSecondary}; font-size: 15px; line-height: 1.7;">
              {{{EXPLANATION_HTML}}}
            </div>
          </div>
          {{/EXPLANATION_HTML}}

          <div style="margin-top: 36px; padding-top: 24px; border-top: 1px solid ${EMAIL_THEME.divider};">
            <p style="margin: 0; font-size: 13px; color: ${EMAIL_THEME.textSecondary};">
              Don't want these emails? <a href="{{{UNSUBSCRIBE_URL}}}" style="color: ${EMAIL_THEME.badgeText}; text-decoration: none;">Unsubscribe</a>
            </p>
          </div>
        </div>
        <p style="margin: 24px 0 0 0; font-size: 12px; text-align: center; color: ${EMAIL_THEME.muted};">Signals · Automated market signals you can actually read</p>
      </td>
    </tr>
  </table>
</body>
</html>
`.trim();
}

function buildSignalNotificationText(): string {
  return `New {{{SIGNAL_TYPE}}} signal for {{{SYMBOL}}}

Generated at: {{{TIMESTAMP}}}
Strength: {{{STRENGTH}}} / 100
Price at signal: $\${{{PRICE}}}

Key Factors:
{{{REASONING_TEXT}}}

{{#EXPLANATION_TEXT}}
Analysis:
{{{EXPLANATION_TEXT}}}
{{/EXPLANATION_TEXT}}

---
Unsubscribe: {{{UNSUBSCRIBE_URL}}}

Signals - Automated market signals you can actually read`;
}
