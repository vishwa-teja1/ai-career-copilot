import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import type { CandidateProfile, ResumeUploadResponse, User } from "@/lib/types";

export function useCurrentUser() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const setUser = useAuthStore((s) => s.setUser);

  return useQuery({
    queryKey: ["me"],
    enabled: !!accessToken,
    queryFn: async () => {
      const { data } = await api.get<User>("/auth/me");
      setUser(data);
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useCandidateProfile() {
  const accessToken = useAuthStore((s) => s.accessToken);

  return useQuery({
    queryKey: ["profile"],
    enabled: !!accessToken,
    queryFn: async () => {
      const { data } = await api.get<CandidateProfile>("/profile/me");
      return data;
    },
    retry: (failureCount, error: any) => {
      // 404 just means "no resume uploaded yet" - not worth retrying.
      if (error?.response?.status === 404) return false;
      return failureCount < 2;
    },
  });
}

export function useUploadResume() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await api.post<ResumeUploadResponse>("/resume/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: Partial<CandidateProfile>) => {
      const { data } = await api.patch<CandidateProfile>("/profile/me", payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}
