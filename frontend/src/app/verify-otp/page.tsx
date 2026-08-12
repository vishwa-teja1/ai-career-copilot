"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AuthShell } from "@/components/auth-shell";
import { Button } from "@/components/ui/button";
import { FormField, Input } from "@/components/ui/input";
import { api, extractErrorMessage } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";

function VerifyOTPForm() {
  const router = useRouter();
  const params = useSearchParams();
  const email = params.get("email") || "";
  const setTokens = useAuthStore((s) => s.setTokens);

  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [resent, setResent] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { data } = await api.post("/auth/verify-otp", { email, code });
      setTokens(data.access_token, data.refresh_token);
      router.push("/dashboard/resume");
    } catch (err) {
      setError(extractErrorMessage(err, "That code didn't work. Check the digits and try again."));
    } finally {
      setLoading(false);
    }
  }

  async function handleResend() {
    setResent(false);
    await api.post("/auth/resend-otp", { email }).catch(() => {});
    setResent(true);
  }

  return (
    <AuthShell
      eyebrow="Step 2 of 3"
      title="Verify your email"
      subtitle={`We sent a 6-digit code to ${email || "your email"}.`}
    >
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <FormField label="Verification code" htmlFor="code">
          <Input
            id="code"
            required
            inputMode="numeric"
            maxLength={6}
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
            placeholder="000000"
            className="text-center text-2xl tracking-[0.5em]"
          />
        </FormField>

        {error && (
          <div className="rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>
        )}

        <Button type="submit" loading={loading} className="mt-2 w-full" disabled={code.length !== 6}>
          Verify &amp; continue
        </Button>
      </form>

      <button onClick={handleResend} className="mt-6 w-full text-center text-sm text-muted hover:text-accent">
        {resent ? "New code sent - check your inbox." : "Didn't get a code? Resend"}
      </button>
    </AuthShell>
  );
}

export default function VerifyOTPPage() {
  return (
    <Suspense fallback={null}>
      <VerifyOTPForm />
    </Suspense>
  );
}
