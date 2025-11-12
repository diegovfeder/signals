/**
 * Email templates registry for Signals
 *
 * All templates are stored here and can be synced to Resend via the API route
 */

import { confirmationEmailTemplate } from "./confirmation";
import { reactivationEmailTemplate } from "./reactivation";
import { signalNotificationTemplate } from "./signal-notification";
import type { EmailTemplate } from "./types";

/**
 * All email templates available in the system
 */
export const EMAIL_TEMPLATES: EmailTemplate[] = [
  confirmationEmailTemplate,
  reactivationEmailTemplate,
  signalNotificationTemplate,
];

export * from "./types";
export * from "./theme";
export { confirmationEmailTemplate } from "./confirmation";
export { reactivationEmailTemplate } from "./reactivation";
export { signalNotificationTemplate } from "./signal-notification";
