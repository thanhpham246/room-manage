import { BuildingForm } from "@/features/buildings/building-form";
import { getUsers } from "@/lib/api/server";

export default async function CreateBuildingPage() {
  const users = await getUsers();
  const staffUsers = users.filter((user) => user.role === "staff" && user.is_active);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Thêm nhà</h1>
        <p className="mt-1 text-sm text-slate-500">
          Khai báo thông tin nhà, số tầng và số phòng theo từng tầng.
        </p>
      </div>
      <BuildingForm mode="create" staffUsers={staffUsers} />
    </div>
  );
}
