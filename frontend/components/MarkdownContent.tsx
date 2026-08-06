import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CopyButton } from "./CopyButton";

/**
 * Renders assistant message content as Markdown.
 *
 * Custom component overrides keep the styling consistent with the
 * rest of the interface (Geist Mono for code, the accent color for
 * links) rather than react-markdown's unstyled defaults. This is
 * where future RAG responses' formatted content (headings, lists,
 * citations) will render.
 */
export function MarkdownContent({ content }: { content: string }) {
  return (
    <div className="prose-vision">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
          ul: ({ children }) => (
            <ul className="mb-3 list-disc space-y-1 pl-5 last:mb-0">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="mb-3 list-decimal space-y-1 pl-5 last:mb-0">{children}</ol>
          ),
          h1: ({ children }) => (
            <h1 className="mb-2 mt-4 text-lg font-semibold first:mt-0">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="mb-2 mt-4 text-base font-semibold first:mt-0">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="mb-2 mt-3 text-sm font-semibold first:mt-0">{children}</h3>
          ),
          a: ({ children, href }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--accent)] underline decoration-[var(--accent)]/40 underline-offset-2 hover:decoration-[var(--accent)]"
            >
              {children}
            </a>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-[var(--foreground)]">{children}</strong>
          ),
          code: ({ className, children, ...props }) => {
            const isBlock = className?.includes("language-");
            if (!isBlock) {
              return (
                <code
                  className="rounded bg-[var(--surface-hover)] px-1.5 py-0.5 font-mono text-[0.85em]"
                  {...props}
                >
                  {children}
                </code>
              );
            }
            return (
              <code className={`font-mono text-[0.85em] ${className ?? ""}`} {...props}>
                {children}
              </code>
            );
          },
          pre: ({ children }) => {
            const codeText = extractText(children);
            return (
              <div className="group relative mb-3 last:mb-0">
                <pre className="overflow-x-auto rounded-lg border border-[var(--border)] bg-[var(--surface-hover)] p-3">
                  {children}
                </pre>
                <div className="absolute right-2 top-2 opacity-0 transition-opacity group-hover:opacity-100">
                  <CopyButton text={codeText} compact />
                </div>
              </div>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

/** Pulls plain text out of a <pre><code>...</code></pre> children tree for the copy button. */
function extractText(node: React.ReactNode): string {
  if (typeof node === "string") return node;
  if (Array.isArray(node)) return node.map(extractText).join("");
  if (
    node &&
    typeof node === "object" &&
    "props" in node &&
    node.props &&
    typeof node.props === "object" &&
    "children" in node.props
  ) {
    return extractText((node.props as { children?: React.ReactNode }).children);
  }
  return "";
}
