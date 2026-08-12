"use client";

import { useState } from "react";
import Link from "next/link";
import { Briefcase, GraduationCap, Award, FolderGit2, Languages, Pencil, Check, X } from "lucide-react";
import { useCandidateProfile, useUpdateProfile } from "@/lib/hooks";
import { Button } from "@/components/ui/button";

function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: React.ElementType;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-xl2 border border-line bg-panel p-6">
      <div className="mb-4 flex items-center gap-2">
        <Icon size={16} className="text-accent" />
        <h2 className="font-display text-sm font-semibold uppercase tracking-wide text-white">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function EditableHeadline({ headline }: { headline: string | null }) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(headline ?? "");
  const update = useUpdateProfile();

  if (!editing) {
    return (
      <div className="flex items-center gap-2">
        <p className="text-sm text-muted">{headline ?? "No headline yet"}</p>
        <button onClick={() => setEditing(true)} className="text-muted hover:text-accent">
          <Pencil size={12} />
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <input
        autoFocus
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className="w-full max-w-md rounded-md border border-line bg-panel2 px-2 py-1 text-sm text-white outline-none focus:border-accent"
      />
      <button
        onClick={() => {
          update.mutate({ headline: value });
          setEditing(false);
        }}
        className="text-accent2"
      >
        <Check size={16} />
      </button>
      <button onClick={() => setEditing(false)} className="text-muted">
        <X size={16} />
      </button>
    </div>
  );
}

export default function ProfilePage() {
  const { data: profile, isLoading, isError, error } = useCandidateProfile();

  if (isLoading) {
    return <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />;
  }

  const notFound = (error as any)?.response?.status === 404;

  if (isError && notFound) {
    return (
      <div className="mx-auto max-w-lg rounded-xl2 border border-line bg-panel p-10 text-center">
        <h1 className="font-display text-xl font-bold text-white">No profile yet</h1>
        <p className="mt-2 text-sm text-muted">Upload your master resume to build your structured candidate profile.</p>
        <Link href="/dashboard/resume">
          <Button className="mt-6">Upload resume</Button>
        </Link>
      </div>
    );
  }

  if (isError || !profile) {
    return <p className="text-sm text-danger">Couldn't load your profile. Please refresh.</p>;
  }

  if (profile.parsing_status === "processing" || profile.parsing_status === "pending") {
    return (
      <div className="mx-auto max-w-lg rounded-xl2 border border-line bg-panel p-10 text-center">
        <div className="mx-auto mb-4 h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
        <p className="text-sm text-white">Still parsing your resume…</p>
        <p className="mt-1 text-xs text-muted">This page will update automatically once it's done.</p>
      </div>
    );
  }

  if (profile.parsing_status === "failed") {
    return (
      <div className="mx-auto max-w-lg rounded-xl2 border border-danger/40 bg-panel p-10 text-center">
        <p className="text-sm text-white">Resume parsing failed.</p>
        <Link href="/dashboard/resume">
          <Button className="mt-6">Try uploading again</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-1">
        <h1 className="font-display text-2xl font-bold text-white">{profile.full_name ?? "Your Profile"}</h1>
        <EditableHeadline headline={profile.headline} />
        <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted">
          {profile.location && <span>{profile.location}</span>}
          {profile.github_url && (
            <a href={profile.github_url} target="_blank" className="text-accent hover:underline">
              GitHub
            </a>
          )}
          {profile.linkedin_url && (
            <a href={profile.linkedin_url} target="_blank" className="text-accent hover:underline">
              LinkedIn
            </a>
          )}
          {profile.portfolio_url && (
            <a href={profile.portfolio_url} target="_blank" className="text-accent hover:underline">
              Portfolio
            </a>
          )}
        </div>
      </div>

      {profile.summary && (
        <section className="mb-6 rounded-xl2 border border-line bg-panel p-6">
          <p className="text-sm leading-relaxed text-muted">{profile.summary}</p>
        </section>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Skills */}
        <Section icon={Award} title="Skills">
          {profile.skills.length === 0 ? (
            <p className="text-sm text-muted">No skills extracted yet.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {profile.skills.map((s) => (
                <span
                  key={s.id}
                  className="rounded-full border border-line bg-panel2 px-3 py-1 text-xs text-white"
                  title={s.proficiency ?? undefined}
                >
                  {s.name}
                </span>
              ))}
            </div>
          )}
        </Section>

        {/* Languages */}
        <Section icon={Languages} title="Languages">
          {!profile.languages_spoken || profile.languages_spoken.length === 0 ? (
            <p className="text-sm text-muted">None listed.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {profile.languages_spoken.map((l) => (
                <span key={l} className="rounded-full border border-line bg-panel2 px-3 py-1 text-xs text-white">
                  {l}
                </span>
              ))}
            </div>
          )}
        </Section>

        {/* Experience + Internships */}
        <Section icon={Briefcase} title="Experience">
          {profile.experiences.length === 0 && profile.internships.length === 0 ? (
            <p className="text-sm text-muted">No experience listed.</p>
          ) : (
            <div className="flex flex-col gap-4">
              {profile.experiences.map((exp) => (
                <div key={exp.id}>
                  <p className="text-sm font-medium text-white">
                    {exp.title} · {exp.company}
                  </p>
                  <p className="text-xs text-muted">
                    {exp.start_date ?? "?"} – {exp.is_current ? "Present" : exp.end_date ?? "?"}
                  </p>
                  {exp.description && <p className="mt-1 text-xs text-muted">{exp.description}</p>}
                </div>
              ))}
              {profile.internships.map((intern) => (
                <div key={intern.id}>
                  <p className="text-sm font-medium text-white">
                    {intern.role} · {intern.organization}
                  </p>
                  <p className="text-xs text-muted">
                    {intern.start_date ?? "?"} – {intern.end_date ?? "?"}
                  </p>
                  {intern.description && <p className="mt-1 text-xs text-muted">{intern.description}</p>}
                </div>
              ))}
            </div>
          )}
        </Section>

        {/* Education */}
        <Section icon={GraduationCap} title="Education">
          {profile.education.length === 0 ? (
            <p className="text-sm text-muted">No education listed.</p>
          ) : (
            <div className="flex flex-col gap-4">
              {profile.education.map((ed) => (
                <div key={ed.id}>
                  <p className="text-sm font-medium text-white">{ed.institution}</p>
                  <p className="text-xs text-muted">
                    {ed.degree}
                    {ed.field_of_study ? ` · ${ed.field_of_study}` : ""}
                  </p>
                  <p className="text-xs text-muted">
                    {ed.start_date ?? "?"} – {ed.end_date ?? "?"} {ed.grade ? `· ${ed.grade}` : ""}
                  </p>
                </div>
              ))}
            </div>
          )}
        </Section>

        {/* Projects */}
        <Section icon={FolderGit2} title="Projects">
          {profile.projects.length === 0 ? (
            <p className="text-sm text-muted">No projects listed.</p>
          ) : (
            <div className="flex flex-col gap-4">
              {profile.projects.map((p) => (
                <div key={p.id}>
                  <p className="text-sm font-medium text-white">
                    {p.url ? (
                      <a href={p.url} target="_blank" className="hover:text-accent hover:underline">
                        {p.title}
                      </a>
                    ) : (
                      p.title
                    )}
                  </p>
                  {p.description && <p className="mt-1 text-xs text-muted">{p.description}</p>}
                  {p.tech_stack && p.tech_stack.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {p.tech_stack.map((t) => (
                        <span key={t} className="rounded bg-panel2 px-2 py-0.5 text-[10px] text-muted">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </Section>

        {/* Certifications + Achievements */}
        <Section icon={Award} title="Certifications & Achievements">
          {profile.certifications.length === 0 && profile.achievements.length === 0 ? (
            <p className="text-sm text-muted">None listed.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {profile.certifications.map((c) => (
                <div key={c.id}>
                  <p className="text-sm text-white">{c.name}</p>
                  <p className="text-xs text-muted">{c.issuer}</p>
                </div>
              ))}
              {profile.achievements.map((a) => (
                <div key={a.id}>
                  <p className="text-sm text-white">{a.title}</p>
                  {a.description && <p className="text-xs text-muted">{a.description}</p>}
                </div>
              ))}
            </div>
          )}
        </Section>
      </div>
    </div>
  );
}
