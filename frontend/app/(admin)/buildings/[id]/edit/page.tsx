import { notFound } from "next/navigation";

import { BuildingForm } from "@/features/buildings/building-form";
import { getBuilding, getUsers } from "@/lib/api/server";

export default async function EditBuildingPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [building, users] = await Promise.all([getBuilding(Number(id)), getUsers()]);
  if (!building) {
    notFound();
  }
  const staffUsers = users.filter((user) => user.role === "staff" && user.is_active);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Sửa nhà</h1>
        <p className="mt-1 text-sm text-slate-500">
          Cập nhật thông tin vận hành, liên hệ, tiện ích và chi phí chung.
        </p>
      </div>
      <BuildingForm building={building} mode="edit" staffUsers={staffUsers} />
    </div>
  );
}
