/**
 * Email templates registry for Signals
 *
 * All templates are stored here and can be synced to Resend via the API route
 */

import { confirmationEmailTemplate } from "./templates/confirmation";
import { reactivationEmailTemplate } from "./templates/reactivation";
import { signalNotificationTemplate } from "./templates/signal-notification";
import type { EmailTemplate } from "./templates/types";

/**
 * All email templates available in the system
 */
export const EMAIL_TEMPLATES: EmailTemplate[] = [
  confirmationEmailTemplate,
  reactivationEmailTemplate,
  signalNotificationTemplate,
];

export * from "./templates/types";
export * from "./templates/theme";
export { confirmationEmailTemplate } from "./templates/confirmation";
export { reactivationEmailTemplate } from "./templates/reactivation";
export { signalNotificationTemplate } from "./templates/signal-notification";
