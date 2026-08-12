"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AuthShell } from "@/components/auth-shell";
import { Button } from "@/components/ui/button";
import { FormField, Input } from "@/components/ui/input";
import { api, extractErrorMessage } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";

export default function LoginPage() {
  const router = useRouter();
  const setTokens = useAuthStore((s) => s.setTokens);
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", form);
      setTokens(data.access_token, data.refresh_token);
      router.push("/dashboard/profile");
    } catch (err) {
      setError(extractErrorMessage(err, "Incorrect email or password."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell eyebrow="Welcome back" title="Log in" subtitle="Pick up where you left off.">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <FormField label="Email" htmlFor="email">
          <Input
            id="email"
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="you@example.com"
          />
        </FormField>
        <FormField label="Password" htmlFor="password">
          <Input
            id="password"
            type="password"
            required
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            placeholder="••••••••"
          />
        </FormField>

        {error && (
          <div className="rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>
        )}

        <Button type="submit" loading={loading} className="mt-2 w-full">
          Log in
        </Button>
      </form>

      <div className="mt-6 flex items-center gap-3 text-xs text-muted">
        <div className="h-px flex-1 bg-line" />
        or continue with
        <div className="h-px flex-1 bg-line" />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <Button variant="ghost" type="button" className="w-full" disabled>
          Google
        </Button>
        <Button variant="ghost" type="button" className="w-full" disabled>
          GitHub
        </Button>
      </div>

      <p className="mt-6 text-center text-sm text-muted">
        New here?{" "}
        <Link href="/register" className="font-medium text-accent hover:underline">
          Create an account
        </Link>
      </p>
    </AuthShell>
  );
}
