'use client';

import React, { useEffect, useState } from 'react';
import { tokenStorage } from './tokenStorage';

interface AuthGuardProps {
  allowedRoles?: string[];
  redirectUrl?: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({
  allowedRoles = [],
  redirectUrl = '/login',
  children,
  fallback = null
}) => {
  const [authorized, setAuthorized] = useState<boolean | null>(null);

  useEffect(() => {
    const token = tokenStorage.getAccessToken();
    const user = tokenStorage.getUserSession<{ role?: string }>();

    if (!token || !user) {
      setAuthorized(false);
      if (typeof window !== 'undefined') window.location.href = redirectUrl;
      return;
    }

    if (allowedRoles.length > 0 && user.role && !allowedRoles.includes(user.role)) {
      setAuthorized(false);
      if (typeof window !== 'undefined') window.location.href = '/unauthorized';
      return;
    }

    setAuthorized(true);
  }, [allowedRoles, redirectUrl]);

  if (authorized === null) {
    return (
      fallback || (
        <div className="flex h-screen w-full items-center justify-center bg-[#0B1313]">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#1D6F72] border-r-transparent" />
        </div>
      )
    );
  }

  if (!authorized) return null;

  return <>{children}</>;
};
