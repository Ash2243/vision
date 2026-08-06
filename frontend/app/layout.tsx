import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vision",
  description: "AI that understands websites.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <body className="h-full min-h-full">{children}</body>
    </html>
  );
}
