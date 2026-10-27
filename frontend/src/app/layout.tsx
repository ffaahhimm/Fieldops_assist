import type { Metadata } from 'next';
import './globals.css';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: 'FieldOps Assist — IT & Security Field Service Platform',
  description:
    'IT & Security Field Service Platform with AI Troubleshooting. Diagnose Faster. Manage Smarter. Resolve Better.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
