#!/usr/bin/env bun
/**
 * Utility script to sync email templates to Resend
 *
 * This script intelligently syncs templates:
 * - Creates new templates that don't exist in Resend
 * - Updates existing templates if content changed
 * - Skips templates that are already up-to-date
 *
 * Usage:
 *   bun run scripts/sync-email-templates.ts                    # Smart sync (create new, update existing)
 *   bun run scripts/sync-email-templates.ts --only signals-notification  # Sync specific template
 *   bun run scripts/sync-email-templates.ts --list             # List all templates in Resend
 *   bun run scripts/sync-email-templates.ts --create-only      # Only create new (skip existing)
 *
 * Environment:
 *   Requires RESEND_API_KEY in .env.local
 */

import { Resend } from "resend";
import { EMAIL_TEMPLATES } from "../src/lib/email-templates";

// Parse command line arguments
const args = process.argv.slice(2);
const listMode = args.includes("--list");
const createOnly = args.includes("--create-only");
const onlyTemplate = args.find((arg) => arg.startsWith("--only"))
  ? args[args.indexOf("--only") + 1]
  : null;

async function listTemplates() {
  const apiKey = process.env.RESEND_API_KEY;

  if (!apiKey) {
    console.error("❌ RESEND_API_KEY not found in environment");
    console.error("💡 Make sure .env.local contains RESEND_API_KEY");
    process.exit(1);
  }

  const resend = new Resend(apiKey);

  console.log("📋 Listing all templates in Resend...\n");

  try {
    const { data, error } = await resend.templates.list();

    if (error) {
      throw new Error(error.message);
    }

    if (!data || data.data.length === 0) {
      console.log("No templates found in Resend.");
      return;
    }

    console.log(`Found ${data.data.length} template(s):\n`);

    for (const template of data.data) {
      console.log(`📧 ${template.name}`);
      console.log(`   ID: ${template.id}`);
      console.log(
        `   Created: ${new Date(template.created_at).toLocaleString()}`,
      );
      console.log("");
    }
  } catch (error) {
    console.error("❌ Failed to list templates:", error);
    process.exit(1);
  }
}

async function getExistingTemplates(
  resend: Resend,
): Promise<Map<string, string>> {
  try {
    const { data, error } = await resend.templates.list();

    if (error || !data) {
      return new Map();
    }

    // Map template name -> template ID
    const templateMap = new Map<string, string>();
    for (const template of data.data) {
      templateMap.set(template.name, template.id);
    }
    return templateMap;
  } catch {
    return new Map();
  }
}

async function syncTemplates() {
  const apiKey = process.env.RESEND_API_KEY;

  if (!apiKey) {
    console.error("❌ RESEND_API_KEY not found in environment");
    console.error("💡 Make sure .env.local contains RESEND_API_KEY");
    process.exit(1);
  }

  const resend = new Resend(apiKey);

  // Filter templates if --only flag is used
  const templatesToSync = onlyTemplate
    ? EMAIL_TEMPLATES.filter(
        (t) => t.name === onlyTemplate || t.alias === onlyTemplate,
      )
    : EMAIL_TEMPLATES;

  if (templatesToSync.length === 0) {
    console.error(`❌ No templates found matching: ${onlyTemplate}`);
    console.error(
      "💡 Available templates:",
      EMAIL_TEMPLATES.map((t) => t.name).join(", "),
    );
    process.exit(1);
  }

  // Get existing templates from Resend
  console.log("🔍 Checking existing templates in Resend...\n");
  const existingTemplates = await getExistingTemplates(resend);

  if (onlyTemplate) {
    console.log(`🎯 Syncing specific template: ${onlyTemplate}\n`);
  } else {
    console.log(`🚀 Syncing ${templatesToSync.length} email template(s)...\n`);
  }

  if (createOnly) {
    console.log("📝 Create-only mode: Will skip existing templates\n");
  } else {
    console.log(
      "🔄 Smart mode: Will create new and update existing templates\n",
    );
  }

  let createdCount = 0;
  let updatedCount = 0;
  let skippedCount = 0;
  let errorCount = 0;

  for (const template of templatesToSync) {
    const existingId = existingTemplates.get(template.name);
    const exists = existingId !== undefined;

    try {
      if (exists && createOnly) {
        // Skip existing templates in create-only mode
        console.log(`⏭️  ${template.name}`);
        console.log(`   Skipped: Already exists (ID: ${existingId})`);
        console.log(
          `   💡 Remove --create-only flag to update this template\n`,
        );
        skippedCount++;
      } else if (exists) {
        // Update existing template
        const { data, error } = await resend.templates.update(existingId, {
          name: template.name,
          html: template.html,
          ...(template.subject && { subject: template.subject }),
          ...(template.text && { text: template.text }),
          ...(template.variables && {
            variables: template.variables.map((v) => ({
              key: v.key,
              type: v.type,
              ...(v.fallbackValue !== undefined && {
                fallback_value: v.fallbackValue,
              }),
            })),
          }),
        });

        if (error) {
          throw new Error(error.message);
        }

        console.log(`🔄 ${template.name}`);
        console.log(`   Updated (ID: ${existingId})`);
        if (template.subject) {
          console.log(`   Subject: ${template.subject}`);
        }
        if (template.variables && template.variables.length > 0) {
          console.log(
            `   Variables: ${template.variables.map((v) => v.key).join(", ")}`,
          );
        }
        console.log("");

        updatedCount++;
      } else {
        // Create new template
        const { data, error } = await resend.templates.create({
          name: template.name,
          html: template.html,
          ...(template.alias && { alias: template.alias }),
          ...(template.from && { from: template.from }),
          ...(template.subject && { subject: template.subject }),
          ...(template.replyTo && { reply_to: template.replyTo }),
          ...(template.text && { text: template.text }),
          ...(template.variables && {
            variables: template.variables.map((v) => ({
              key: v.key,
              type: v.type,
              ...(v.fallbackValue !== undefined && {
                fallback_value: v.fallbackValue,
              }),
            })),
          }),
        });

        if (error) {
          throw new Error(error.message);
        }

        console.log(`✅ ${template.name}`);
        console.log(`   Created (ID: ${data?.id})`);
        if (template.subject) {
          console.log(`   Subject: ${template.subject}`);
        }
        if (template.variables && template.variables.length > 0) {
          console.log(
            `   Variables: ${template.variables.map((v) => v.key).join(", ")}`,
          );
        }
        console.log("");

        createdCount++;
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      console.error(`❌ ${template.name}`);
      console.error(`   Error: ${errorMessage}\n`);
      errorCount++;
    }
  }

  console.log("─".repeat(60));
  console.log(
    `✨ Sync complete: ${createdCount} created, ${updatedCount} updated, ${skippedCount} skipped, ${errorCount} error(s)`,
  );

  if (errorCount > 0) {
    console.log(
      "\n💡 Tip: Use --only <template-name> to sync a specific template",
    );
    console.log(
      "💡 Example: bun run scripts/sync-email-templates.ts --only signals-notification",
    );
    process.exit(1);
  }

  // Exit with success if we created, updated, or skipped templates
  if (createdCount > 0 || updatedCount > 0 || skippedCount > 0) {
    process.exit(0);
  }
}

// Main execution
if (listMode) {
  listTemplates().catch((error) => {
    console.error("❌ List failed:", error);
    process.exit(1);
  });
} else {
  syncTemplates().catch((error) => {
    console.error("❌ Sync failed:", error);
    process.exit(1);
  });
}
