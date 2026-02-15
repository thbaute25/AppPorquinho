"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { Usuario } from "@/lib/types";

interface AuthContextType {
  usuario: Usuario | null;
  token: string | null;
  loginUser: (token: string, usuario: Usuario) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  usuario: null,
  token: null,
  loginUser: () => {},
  logout: () => {},
  isLoading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("usuario");
    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUsuario(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem("token");
        localStorage.removeItem("usuario");
      }
    }
    setIsLoading(false);
  }, []);

  const loginUser = (newToken: string, newUsuario: Usuario) => {
    localStorage.setItem("token", newToken);
    localStorage.setItem("usuario", JSON.stringify(newUsuario));
    setToken(newToken);
    setUsuario(newUsuario);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    setToken(null);
    setUsuario(null);
  };

  return (
    <AuthContext.Provider value={{ usuario, token, loginUser, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
