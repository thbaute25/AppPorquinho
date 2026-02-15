"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { login, register } from "@/lib/api";
import Logo from "@/components/Logo";

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [senha2, setSenha2] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const { loginUser, usuario, isLoading } = useAuth();
  const router = useRouter();

  // Redirecionar se ja logado
  if (!isLoading && usuario) {
    router.push("/dashboard");
    return null;
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!email || !senha) {
      setError("Preencha todos os campos!");
      return;
    }

    setLoading(true);
    try {
      const res = await login(email, senha);
      loginUser(res.token, res.usuario);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao fazer login");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!nome || !email || !senha) {
      setError("Preencha todos os campos!");
      return;
    }
    if (senha.length < 6) {
      setError("A senha deve ter no minimo 6 caracteres!");
      return;
    }
    if (senha !== senha2) {
      setError("As senhas nao coincidem!");
      return;
    }

    setLoading(true);
    try {
      const res = await register(nome, email, senha);
      loginUser(res.token, res.usuario);
      setSuccess("Conta criada com sucesso!");
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao criar conta");
    } finally {
      setLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-app-text-light">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-app-bg">
      <div className="w-full max-w-md">
        <div className="login-container">
          <Logo width={130} />
          <h1
            className="text-3xl font-extrabold mt-4 mb-1"
            style={{
              background: "linear-gradient(135deg, #FF6B8A 0%, #6C5CE7 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Porquinho
          </h1>
          <p className="text-app-text-light mb-6">Suas financas de um jeito simples</p>
        </div>

        <div className="mt-6">
          {isLogin ? (
            <form onSubmit={handleLogin} className="form-card">
              <h2 className="text-lg font-semibold mb-4">Entrar na sua conta</h2>

              <div className="space-y-3">
                <input
                  type="email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field"
                />
                <input
                  type="password"
                  placeholder="Sua senha"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  className="input-field"
                />
              </div>

              {error && (
                <div className="mt-3 p-3 bg-red-50 text-red-600 rounded-xl text-sm">{error}</div>
              )}

              <button type="submit" className="btn-primary mt-4" disabled={loading}>
                {loading ? "Entrando..." : "Entrar"}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="form-card">
              <h2 className="text-lg font-semibold mb-4">Criar nova conta</h2>

              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Seu nome completo"
                  value={nome}
                  onChange={(e) => setNome(e.target.value)}
                  className="input-field"
                />
                <input
                  type="email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field"
                />
                <input
                  type="password"
                  placeholder="Minimo 6 caracteres"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  className="input-field"
                />
                <input
                  type="password"
                  placeholder="Repita a senha"
                  value={senha2}
                  onChange={(e) => setSenha2(e.target.value)}
                  className="input-field"
                />
              </div>

              {error && (
                <div className="mt-3 p-3 bg-red-50 text-red-600 rounded-xl text-sm">{error}</div>
              )}
              {success && (
                <div className="mt-3 p-3 bg-green-50 text-green-600 rounded-xl text-sm">{success}</div>
              )}

              <button type="submit" className="btn-primary mt-4" disabled={loading}>
                {loading ? "Criando conta..." : "Criar conta"}
              </button>
            </form>
          )}

          <div className="text-center mt-4">
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                setError("");
                setSuccess("");
              }}
              className="text-primary font-medium hover:underline"
            >
              {isLogin ? "Criar uma conta" : "Ja tenho conta"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
