"use client";

import { AlertTriangle, Save } from "lucide-react";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { browserApiPatch, browserApiPost } from "@/lib/api/client";
import type { Tenant } from "@/lib/api/types";

export function TenantForm({ mode, tenant }: { mode: "create" | "edit"; tenant?: Tenant }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const formData = new FormData(event.currentTarget);
    const payload = {
      full_name: String(formData.get("full_name") || ""),
      phone: String(formData.get("phone") || ""),
      email: valueOrNull(formData.get("email")),
      zalo: valueOrNull(formData.get("zalo")),
      date_of_birth: valueOrNull(formData.get("date_of_birth")),
      gender: valueOrNull(formData.get("gender")),
      identity_type: valueOrNull(formData.get("identity_type")),
      identity_number: valueOrNull(formData.get("identity_number")),
      identity_issued_date: valueOrNull(formData.get("identity_issued_date")),
      identity_issued_place: valueOrNull(formData.get("identity_issued_place")),
      permanent_address: valueOrNull(formData.get("permanent_address")),
      current_address: valueOrNull(formData.get("current_address")),
      emergency_contact_name: valueOrNull(formData.get("emergency_contact_name")),
      emergency_contact_phone: valueOrNull(formData.get("emergency_contact_phone")),
      emergency_contact_relationship: valueOrNull(formData.get("emergency_contact_relationship")),
      note: valueOrNull(formData.get("note")),
    };

    try {
      const result =
        mode === "create"
          ? await browserApiPost<Tenant>("/tenants", payload)
          : await browserApiPatch<Tenant>(`/tenants/${tenant?.id}`, payload);
      router.push(`/tenants/${result.id}`);
      router.refresh();
    } catch {
      setError("Không lưu được hồ sơ người thuê. Kiểm tra dữ liệu và thử lại.");
    }
  }

  return (
    <form className="space-y-6" onSubmit={onSubmit}>
      <Card>
        <h2 className="text-base font-semibold text-ink">Thông tin cơ bản</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {mode === "edit" ? <ReadOnlyField label="Mã người thuê" value={tenant?.tenant_code ?? ""} /> : null}
          <Field label="Họ tên" name="full_name" defaultValue={tenant?.full_name} required />
          <Field label="Số điện thoại" name="phone" defaultValue={tenant?.phone} required />
          <Field label="Email" name="email" defaultValue={tenant?.email} type="email" />
          <Field label="Zalo" name="zalo" defaultValue={tenant?.zalo} />
          <Field label="Ngày sinh" name="date_of_birth" defaultValue={tenant?.date_of_birth} type="date" />
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-500">Giới tính</span>
            <select
              className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
              defaultValue={tenant?.gender ?? ""}
              name="gender"
            >
              <option value="">Chưa chọn</option>
              <option value="male">Nam</option>
              <option value="female">Nữ</option>
              <option value="other">Khác</option>
            </select>
          </label>
        </div>
      </Card>

      <Card>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <h2 className="text-base font-semibold text-ink">Giấy tờ định danh</h2>
          {tenant?.identity_edit_warning ? (
            <div className="inline-flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700">
              <AlertTriangle className="size-4" />
              Người thuê đang có hợp đồng hoạt động. Hãy kiểm tra kỹ trước khi đổi CCCD/CMND.
            </div>
          ) : null}
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-500">Loại giấy tờ</span>
            <select
              className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
              defaultValue={tenant?.identity_type ?? ""}
              name="identity_type"
            >
              <option value="">Chưa chọn</option>
              <option value="cccd">CCCD</option>
              <option value="cmnd">CMND</option>
              <option value="passport">Passport</option>
            </select>
          </label>
          <Field label="Số giấy tờ" name="identity_number" defaultValue={tenant?.identity_number} />
          <Field
            label="Ngày cấp"
            name="identity_issued_date"
            defaultValue={tenant?.identity_issued_date}
            type="date"
          />
          <Field
            label="Nơi cấp"
            name="identity_issued_place"
            defaultValue={tenant?.identity_issued_place}
          />
        </div>
      </Card>

      <Card>
        <h2 className="text-base font-semibold text-ink">Địa chỉ và liên hệ khẩn cấp</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <Field
            label="Địa chỉ thường trú"
            name="permanent_address"
            defaultValue={tenant?.permanent_address}
          />
          <Field
            label="Địa chỉ hiện tại"
            name="current_address"
            defaultValue={tenant?.current_address}
          />
          <Field
            label="Người liên hệ khẩn cấp"
            name="emergency_contact_name"
            defaultValue={tenant?.emergency_contact_name}
          />
          <Field
            label="SĐT khẩn cấp"
            name="emergency_contact_phone"
            defaultValue={tenant?.emergency_contact_phone}
          />
          <Field
            label="Quan hệ"
            name="emergency_contact_relationship"
            defaultValue={tenant?.emergency_contact_relationship}
          />
        </div>
      </Card>

      <Card>
        <label className="space-y-1">
          <span className="text-xs font-medium text-slate-500">Ghi chú</span>
          <textarea
            className="min-h-24 w-full rounded-md border border-border px-3 py-2 text-sm"
            defaultValue={tenant?.note ?? ""}
            name="note"
          />
        </label>
      </Card>

      {error ? <p className="text-sm text-rose-600">{error}</p> : null}
      <Button type="submit">
        <Save className="size-4" />
        Lưu hồ sơ
      </Button>
    </form>
  );
}

function Field({
  defaultValue,
  label,
  name,
  required,
  type = "text",
}: {
  defaultValue?: string | null;
  label: string;
  name: string;
  required?: boolean;
  type?: "text" | "email" | "date";
}) {
  return (
    <label className="space-y-1">
      <span className="text-xs font-medium text-slate-500">{label}</span>
      <Input defaultValue={defaultValue ?? ""} name={name} required={required} type={type} />
    </label>
  );
}

function ReadOnlyField({ label, value }: { label: string; value: string }) {
  return (
    <label className="space-y-1">
      <span className="text-xs font-medium text-slate-500">{label}</span>
      <Input readOnly value={value} />
    </label>
  );
}

function valueOrNull(value: FormDataEntryValue | null) {
  const text = String(value || "").trim();
  return text.length > 0 ? text : null;
}
