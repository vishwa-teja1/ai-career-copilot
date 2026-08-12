export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_email_verified: boolean;
}

export interface Skill {
  id: string;
  name: string;
  category: string | null;
  proficiency: string | null;
}

export interface Experience {
  id: string;
  company: string;
  title: string;
  location: string | null;
  start_date: string | null;
  end_date: string | null;
  is_current: boolean;
  description: string | null;
  bullet_points: string[] | null;
}

export interface Internship {
  id: string;
  organization: string;
  role: string;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
}

export interface Education {
  id: string;
  institution: string;
  degree: string;
  field_of_study: string | null;
  start_date: string | null;
  end_date: string | null;
  grade: string | null;
}

export interface ProjectItem {
  id: string;
  title: string;
  description: string | null;
  tech_stack: string[] | null;
  url: string | null;
}

export interface Certification {
  id: string;
  name: string;
  issuer: string | null;
  issue_date: string | null;
  credential_url: string | null;
}

export interface Achievement {
  id: string;
  title: string;
  description: string | null;
  date: string | null;
}

export type ParsingStatus = "pending" | "processing" | "completed" | "failed";

export interface CandidateProfile {
  id: string;
  full_name: string | null;
  headline: string | null;
  location: string | null;
  summary: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  languages_spoken: string[] | null;
  parsing_status: ParsingStatus;
  skills: Skill[];
  experiences: Experience[];
  internships: Internship[];
  education: Education[];
  projects: ProjectItem[];
  certifications: Certification[];
  achievements: Achievement[];
}

export interface ResumeUploadResponse {
  resume_version_id: string;
  profile_id: string;
  parsing_status: ParsingStatus;
  message: string;
}
