"use client";

import { useRef, useState } from "react";
import { FileText, Loader2, UploadCloud, CheckCircle2, AlertCircle } from "lucide-react";
import { useCandidateProfile, useUploadResume } from "@/lib/hooks";
import { extractErrorMessage } from "@/lib/api";
import { Button } from "@/components/ui/button";

const ACCEPTED_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

export default function ResumeUploadPage() {
  const { data: profile, isLoading: profileLoading } = useCandidateProfile();
  const upload = useUploadResume();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  function handleFile(file: File | undefined) {
    setLocalError(null);
    if (!file) return;
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setLocalError("Only PDF and DOCX files are supported.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setLocalError("File is larger than the 5MB limit.");
      return;
    }
    upload.mutate(file);
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="font-display text-2xl font-bold text-white">Master Resume</h1>
      <p className="mt-1 text-sm text-muted">
        Upload one resume. We parse it once into a structured profile that every other feature - matching,
        tailoring, cover letters - reads from. Re-upload any time to refresh it.
      </p>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragActive(false);
          handleFile(e.dataTransfer.files?.[0]);
        }}
        onClick={() => inputRef.current?.click()}
        className={`mt-8 flex cursor-pointer flex-col items-center justify-center rounded-xl2 border-2 border-dashed px-6 py-14 text-center transition-colors ${
          dragActive ? "border-accent bg-accent/5" : "border-line bg-panel hover:border-accent/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".pdf,.docx"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        {upload.isPending ? (
          <>
            <Loader2 className="mb-3 animate-spin text-accent" size={28} />
            <p className="text-sm font-medium text-white">Parsing your resume with AI…</p>
            <p className="mt-1 text-xs text-muted">Extracting skills, experience, and education. This takes a few seconds.</p>
          </>
        ) : (
          <>
            <UploadCloud className="mb-3 text-muted" size={28} />
            <p className="text-sm font-medium text-white">Drag & drop your resume, or click to browse</p>
            <p className="mt-1 text-xs text-muted">PDF or DOCX, up to 5MB</p>
          </>
        )}
      </div>

      {(localError || upload.isError) && (
        <div className="mt-4 flex items-start gap-2 rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-danger">
          <AlertCircle size={16} className="mt-0.5 shrink-0" />
          <span>{localError ?? extractErrorMessage(upload.error, "Upload failed. Please try again.")}</span>
        </div>
      )}

      {upload.isSuccess && (
        <div className="mt-4 flex items-start gap-2 rounded-lg border border-accent2/40 bg-accent2/10 px-4 py-3 text-sm text-accent2">
          <CheckCircle2 size={16} className="mt-0.5 shrink-0" />
          <span>{upload.data.message}</span>
        </div>
      )}

      {!profileLoading && profile && (
        <p className="mt-6 text-xs text-muted">
          Current status:{" "}
          <span className="font-medium text-white">{profile.parsing_status}</span>
        </p>
      )}

      <div className="mt-8 flex items-center gap-3 rounded-lg border border-line bg-panel2/60 px-4 py-3 text-xs text-muted">
        <FileText size={14} className="shrink-0" />
        We never invent skills or experience that aren't in your resume - AI parsing only extracts what's
        actually written, and you can correct anything manually on your Profile page afterward.
      </div>
    </div>
  );
}
