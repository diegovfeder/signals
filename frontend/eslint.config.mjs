import next from "eslint-config-next";

/**
 * Next.js 16 no longer ships the `next lint` CLI wrapper, so we expose the
 * recommended config via the standard ESLint flat-config entry point.
 */
const config = [
  {
    ignores: [
      "public/**",
      "coverage/**",
      "dist/**",
    ],
  },
  ...next,
];

export default config;
