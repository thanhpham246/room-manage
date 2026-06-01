import { TenantForm } from "@/features/tenants/tenant-form";

export default function CreateTenantPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Thêm người thuê</h1>
        <p className="mt-1 text-sm text-slate-500">Tạo hồ sơ người thuê trước khi lập hợp đồng.</p>
      </div>
      <TenantForm mode="create" />
    </div>
  );
}
