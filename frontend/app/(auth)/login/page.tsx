"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Building2, LogIn } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { browserApiPost } from "@/lib/api/client";

const schema = z.object({
  email: z.string().email("Email không hợp lệ"),
  password: z.string().min(8, "Mật khẩu tối thiểu 8 ký tự"),
});

type LoginForm = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const form = useForm<LoginForm>({
    resolver: zodResolver(schema),
    defaultValues: { email: "admin@example.com", password: "password123" },
  });

  async function onSubmit(values: LoginForm) {
    setError(null);
    try {
      await browserApiPost("/auth/login", values);
      router.push("/dashboard");
    } catch {
      setError("Không đăng nhập được. Kiểm tra email hoặc mật khẩu.");
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-stone-50 p-4">
      <Card className="w-full max-w-md">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex size-11 items-center justify-center rounded-lg bg-ink text-white">
            <Building2 className="size-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-ink">NhàTrọ Pro</h1>
            <p className="text-sm text-slate-500">Đăng nhập quản trị</p>
          </div>
        </div>
        <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
          <label className="block space-y-1">
            <span className="text-sm font-medium text-slate-700">Email</span>
            <Input type="email" {...form.register("email")} />
            {form.formState.errors.email ? (
              <span className="text-xs text-rose-600">{form.formState.errors.email.message}</span>
            ) : null}
          </label>
          <label className="block space-y-1">
            <span className="text-sm font-medium text-slate-700">Mật khẩu</span>
            <Input type="password" {...form.register("password")} />
            {form.formState.errors.password ? (
              <span className="text-xs text-rose-600">
                {form.formState.errors.password.message}
              </span>
            ) : null}
          </label>
          {error ? <p className="text-sm text-rose-600">{error}</p> : null}
          <Button className="w-full" type="submit">
            <LogIn className="size-4" />
            Đăng nhập
          </Button>
        </form>
      </Card>
    </main>
  );
}
