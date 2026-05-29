import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Room Manage",
  description: "Apartment and room rental administration",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
