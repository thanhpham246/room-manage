import { notFound } from "next/navigation";

import { TenantForm } from "@/features/tenants/tenant-form";
import { getTenant } from "@/lib/api/server";

export default async function EditTenantPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const tenant = await getTenant(Number(id));
  if (!tenant) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Sửa người thuê</h1>
        <p className="mt-1 text-sm text-slate-500">
          Cập nhật hồ sơ liên hệ, địa chỉ và giấy tờ định danh.
        </p>
      </div>
      <TenantForm mode="edit" tenant={tenant} />
    </div>
  );
}
