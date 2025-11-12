/**
 * Email template types and definitions for Resend integration
 */

export type TemplateVariableType = 'string' | 'number';

export interface TemplateVariable {
  key: string;
  type: TemplateVariableType;
  fallbackValue?: string | number;
}

export interface EmailTemplate {
  name: string;
  alias?: string;
  from?: string;
  subject?: string;
  replyTo?: string | string[];
  html: string;
  text?: string;
  variables?: TemplateVariable[];
}

export interface ResendTemplateResponse {
  id: string;
  object: 'template';
}

export interface ResendTemplateError {
  message: string;
  statusCode: number;
}

/**
 * Template keys for all Signals email templates
 */
export const TEMPLATE_KEYS = {
  CONFIRMATION: 'signals-confirmation',
  REACTIVATION: 'signals-reactivation',
  SIGNAL_NOTIFICATION: 'signals-notification',
} as const;

export type TemplateKey = (typeof TEMPLATE_KEYS)[keyof typeof TEMPLATE_KEYS];
