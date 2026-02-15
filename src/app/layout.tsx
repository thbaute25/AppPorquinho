import type { Metadata } from "next";
import { AuthProvider } from "@/contexts/AuthContext";
import "./globals.css";

export const metadata: Metadata = {
  title: "Porquinho - Financas Pessoais",
  description: "Gerencie suas financas pessoais de forma simples e intuitiva",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-app-bg min-h-screen">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
