import { SimpleCreateForm } from "@/features/resources/simple-create-form";
import { ResourceTable } from "@/features/resources/resource-table";
import { getTenants } from "@/lib/api/server";

export default async function TenantsPage() {
  const tenants = await getTenants();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Người thuê</h1>
        <p className="mt-1 text-sm text-slate-500">Lưu hồ sơ và thông tin liên hệ của người thuê.</p>
      </div>
      <SimpleCreateForm
        endpoint="/tenants"
        fields={[
          { name: "full_name", label: "Họ tên" },
          { name: "phone", label: "Số điện thoại" },
          { name: "email", label: "Email" },
        ]}
        title="Thêm người thuê"
      />
      <ResourceTable
        columns={[
          { key: "full_name", label: "Họ tên" },
          { key: "phone", label: "Số điện thoại" },
          { key: "email", label: "Email" },
        ]}
        items={tenants.items}
      />
    </div>
  );
}
