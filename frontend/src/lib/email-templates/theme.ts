/**
 * Email theme configuration for Signals branded emails
 * Matches the frontend design system from globals.css
 */

export const EMAIL_THEME = {
  // Base colors from design system
  background: "#121212",
  card: "#171717",
  cardBorder: "#292929",
  divider: "#292929",

  // Accent colors
  badgeBg: "#1f1f1f",
  badgeText: "#10b981",

  // Text colors
  textPrimary: "#e2e8f0",
  textSecondary: "#a2a2a2",
  muted: "#898989",

  // Primary green from design system
  primary: "#006239",
  primaryLight: "#007a47",
  primaryDark: "#004d2e",
  primaryForeground: "#dde8e3",

  // Ring/glow color
  ring: "#10b981",

  // Button styling
  buttonGradient:
    "linear-gradient(130deg, #007a47 0%, #006239 50%, #004d2e 100%)",
  buttonShadow:
    "0 2px 8px rgba(0, 0, 0, 0.17), 0 0 20px rgba(16, 185, 129, 0.4)",
  buttonHoverShadow:
    "0 4px 12px rgba(0, 0, 0, 0.17), 0 0 40px rgba(16, 185, 129, 0.6)",
} as const;

/**
 * Build a consistent HTML email wrapper with Signals branding
 */
export const buildEmailHTML = ({
  eyebrow,
  title,
  intro,
  messageLines,
  buttonLabel,
  buttonUrl,
  footnote,
  highlightLabel,
  highlightBody,
}: {
  eyebrow: string;
  title: string;
  intro: string;
  messageLines: string[];
  buttonLabel: string;
  buttonUrl: string;
  footnote: string;
  highlightLabel?: string;
  highlightBody?: string;
}): string => {
  const messageHtml = messageLines
    .map(
      (line) =>
        `<p style="margin: 0 0 16px 0; font-size: 15px; line-height: 1.6; color: ${EMAIL_THEME.textSecondary};">
          ${line}
        </p>`,
    )
    .join("\n");

  const highlightHtml =
    highlightLabel && highlightBody
      ? `
    <div style="margin: 24px 0; padding: 16px 18px; border-radius: 12px; background: ${EMAIL_THEME.badgeBg}; border: 1px solid ${EMAIL_THEME.divider};">
      <p style="margin: 0; font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: ${EMAIL_THEME.muted};">${highlightLabel}</p>
      <p style="margin: 6px 0 0 0; font-size: 15px; color: ${EMAIL_THEME.textPrimary}; font-weight: 500;">${highlightBody}</p>
    </div>
    `
      : "";

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 32px 16px; background: ${EMAIL_THEME.background}; font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
  <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto;">
    <tr>
      <td>
        <div style="background: ${EMAIL_THEME.card}; border: 1px solid ${EMAIL_THEME.cardBorder}; border-radius: 16px; padding: 40px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.17);">
          <p style="margin: 0 0 20px 0; display: inline-block; padding: 6px 12px; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: ${EMAIL_THEME.badgeText}; background: ${EMAIL_THEME.badgeBg}; border-radius: 999px; border: 1px solid ${EMAIL_THEME.divider};">${eyebrow}</p>
          <h1 style="margin: 0 0 12px 0; font-size: 28px; color: ${EMAIL_THEME.textPrimary};">${title}</h1>
          <p style="margin: 0 0 18px 0; font-size: 16px; line-height: 1.6; color: ${EMAIL_THEME.textPrimary};">${intro}</p>
          ${messageHtml}
          ${highlightHtml}
          <div style="text-align: center; margin: 32px 0;">
            <a href="${buttonUrl}" style="display: inline-block; padding: 14px 32px; border-radius: 999px; background: ${EMAIL_THEME.buttonGradient}; border: 1px solid ${EMAIL_THEME.ring}; color: ${EMAIL_THEME.primaryForeground}; font-weight: 600; font-size: 16px; text-decoration: none; box-shadow: ${EMAIL_THEME.buttonShadow}; font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
              ${buttonLabel}
            </a>
          </div>
          <p style="margin: 0 0 8px 0; font-size: 13px; color: ${EMAIL_THEME.muted}; text-align: center;">Can't click the button?</p>
          <p style="margin: 0; font-size: 13px; color: ${EMAIL_THEME.textSecondary}; word-break: break-all; text-align: center;">
            <a href="${buttonUrl}" style="color: ${EMAIL_THEME.badgeText}; text-decoration: none;">${buttonUrl}</a>
          </p>
          <div style="margin-top: 36px; padding-top: 24px; border-top: 1px solid ${EMAIL_THEME.divider};">
            <p style="margin: 0; font-size: 13px; color: ${EMAIL_THEME.textSecondary};">${footnote}</p>
          </div>
        </div>
        <p style="margin: 24px 0 0 0; font-size: 12px; text-align: center; color: ${EMAIL_THEME.muted};">Signals · Automated market signals you can actually read</p>
      </td>
    </tr>
  </table>
</body>
</html>
`.trim();
};
