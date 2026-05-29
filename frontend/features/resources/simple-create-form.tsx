"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { browserApiPost } from "@/lib/api/client";

type FieldConfig = {
  name: string;
  label: string;
  type?: "text" | "number" | "date";
};

export function SimpleCreateForm({
  endpoint,
  fields,
  title,
}: {
  endpoint: string;
  fields: FieldConfig[];
  title: string;
}) {
  const shape: Record<string, z.ZodTypeAny> = {};
  fields.forEach((field) => {
    shape[field.name] =
      field.type === "number"
        ? z.coerce.number().min(0, "Giá trị không hợp lệ")
        : z.string().min(1, "Bắt buộc");
  });
  const schema = z.object(shape);
  const form = useForm<Record<string, unknown>>({
    resolver: zodResolver(schema),
  });

  async function onSubmit(values: Record<string, unknown>) {
    await browserApiPost(endpoint, values);
    window.location.reload();
  }

  return (
    <form
      className="rounded-lg border border-border bg-white p-4 shadow-panel"
      onSubmit={form.handleSubmit(onSubmit)}
    >
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-semibold text-ink">{title}</h2>
        <Button type="submit">
          <Plus className="size-4" />
          Thêm
        </Button>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {fields.map((field) => (
          <label className="space-y-1" key={field.name}>
            <span className="text-xs font-medium text-slate-500">{field.label}</span>
            <Input type={field.type ?? "text"} {...form.register(field.name)} />
            {form.formState.errors[field.name] ? (
              <span className="text-xs text-rose-600">
                {String(form.formState.errors[field.name]?.message)}
              </span>
            ) : null}
          </label>
        ))}
      </div>
    </form>
  );
}
