import Link from "next/link";
import { Github, BarChart3 } from "lucide-react";

export default function Footer() {
  return (
    <footer className="relative bg-[#0a0a0a] py-12 px-4 border-t-2 border-primary/20">
      {/* Green accent line at top */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-linear-to-r from-transparent via-primary to-transparent" />

      <div className="container-app">
        <div className="flex flex-col md:flex-row items-center justify-end gap-6">
          {/* Links */}
          <div className="flex items-center gap-8">
            <Link
              href="/signals"
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-ring transition-colors group"
            >
              <BarChart3 className="size-4 transition-transform group-hover:scale-110" />
              Signals
            </Link>
            <Link
              href="https://github.com/diegovfeder/signals"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-ring transition-colors group"
            >
              <Github className="size-4 transition-transform group-hover:scale-110" />
              GitHub
            </Link>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-6 border-t border-border/40 text-center">
          <p className="text-xs text-muted-foreground/70">
            © {new Date().getFullYear()} SIGNALS - Open source · MIT License.
          </p>
        </div>
      </div>
    </footer>
  );
}
