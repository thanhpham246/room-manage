import { ContractForm } from "@/features/contracts/contract-form";
import { getBuildings, getRooms, getTenants } from "@/lib/api/server";

export default async function CreateContractPage() {
  const [buildings, rooms, tenants] = await Promise.all([
    getBuildings(),
    getRooms(),
    getTenants(),
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Thêm hợp đồng</h1>
        <p className="mt-1 text-sm text-slate-500">
          Chọn người thuê và tài sản thuê. Hệ thống sẽ kiểm tra trùng lịch thuê.
        </p>
      </div>
      <ContractForm
        buildings={buildings.items}
        mode="create"
        rooms={rooms.items}
        tenants={tenants.items}
      />
    </div>
  );
}
