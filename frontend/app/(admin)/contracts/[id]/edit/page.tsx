import { notFound } from "next/navigation";

import { ContractForm } from "@/features/contracts/contract-form";
import { getBuildings, getContract, getRooms, getTenants } from "@/lib/api/server";

export default async function EditContractPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [contract, buildings, rooms, tenants] = await Promise.all([
    getContract(Number(id)),
    getBuildings(),
    getRooms(),
    getTenants(),
  ]);
  if (!contract) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Sửa hợp đồng</h1>
        <p className="mt-1 text-sm text-slate-500">
          Cập nhật hợp đồng theo rule khóa dữ liệu sau khi phát sinh hóa đơn.
        </p>
      </div>
      <ContractForm
        buildings={buildings.items}
        contract={contract}
        mode="edit"
        rooms={rooms.items}
        tenants={tenants.items}
      />
    </div>
  );
}
