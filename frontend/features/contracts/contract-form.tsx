"use client";

import { AlertTriangle, Save } from "lucide-react";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { browserApiPatch, browserApiPost } from "@/lib/api/client";
import type { Building, Contract, Room, Tenant } from "@/lib/api/types";

export function ContractForm({
  buildings,
  contract,
  mode,
  rooms,
  tenants,
}: {
  buildings: Building[];
  contract?: Contract;
  mode: "create" | "edit";
  rooms: Room[];
  tenants: Tenant[];
}) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [scope, setScope] = useState(contract?.scope ?? "room");
  const [selectedBuildingId, setSelectedBuildingId] = useState(
    contract?.building_id ?? buildings[0]?.id ?? 0,
  );
  const lockedByInvoice = mode === "edit" && (contract?.invoice_count ?? 0) > 0;
  const buildingRooms = useMemo(
    () => rooms.filter((room) => room.building_id === selectedBuildingId),
    [rooms, selectedBuildingId],
  );

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const formData = new FormData(event.currentTarget);
    const payload: Record<string, unknown> = {
      scope,
      tenant_id: numberOrNull(formData.get("tenant_id")),
      start_date: String(formData.get("start_date") || ""),
      end_date: valueOrNull(formData.get("end_date")),
      monthly_rent: Number(formData.get("monthly_rent") || 0),
      deposit_amount: Number(formData.get("deposit_amount") || 0),
      note: valueOrNull(formData.get("note")),
    };
    if (scope === "whole_building") {
      payload.building_id = Number(formData.get("building_id") || 0);
      payload.room_id = null;
    } else {
      payload.room_id = Number(formData.get("room_id") || 0);
    }
    if (lockedByInvoice) {
      delete payload.scope;
      delete payload.tenant_id;
      delete payload.building_id;
      delete payload.room_id;
      delete payload.start_date;
      delete payload.monthly_rent;
      delete payload.deposit_amount;
    }

    try {
      const result =
        mode === "create"
          ? await browserApiPost<Contract>("/contracts", payload)
          : await browserApiPatch<Contract>(`/contracts/${contract?.id}`, payload);
      router.push(`/contracts/${result.id}`);
      router.refresh();
    } catch {
      setError("Không lưu được hợp đồng. Kiểm tra dữ liệu, tài sản thuê và khoảng thời gian.");
    }
  }

  return (
    <form className="space-y-6" onSubmit={onSubmit}>
      <Card>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <h2 className="text-base font-semibold text-ink">Thông tin hợp đồng</h2>
          {lockedByInvoice ? (
            <div className="inline-flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700">
              <AlertTriangle className="size-4" />
              Hợp đồng đã có hóa đơn. Tài sản thuê, người thuê, ngày bắt đầu, tiền thuê và cọc bị khóa.
            </div>
          ) : null}
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {mode === "edit" ? <ReadOnlyField label="Mã hợp đồng" value={contract?.contract_code ?? ""} /> : null}
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-500">Loại tài sản thuê</span>
            <select
              className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
              disabled={lockedByInvoice}
              name="scope"
              onChange={(event) => setScope(event.target.value)}
              value={scope}
            >
              <option value="room">Phòng</option>
              <option value="whole_building">Nhà nguyên căn</option>
            </select>
          </label>
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-500">Nhà</span>
            <select
              className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
              disabled={lockedByInvoice || scope === "room"}
              name="building_id"
              onChange={(event) => setSelectedBuildingId(Number(event.target.value))}
              value={selectedBuildingId || ""}
            >
              {buildings.map((building) => (
                <option key={building.id} value={building.id}>
                  {building.code} - {building.name}
                </option>
              ))}
            </select>
          </label>
          {scope === "room" ? (
            <label className="space-y-1">
              <span className="text-xs font-medium text-slate-500">Phòng</span>
              <select
                className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
                defaultValue={contract?.room_id ?? buildingRooms[0]?.id ?? ""}
                disabled={lockedByInvoice}
                name="room_id"
                onChange={(event) => {
                  const room = rooms.find((item) => item.id === Number(event.target.value));
                  if (room) setSelectedBuildingId(room.building_id);
                }}
              >
                {rooms.map((room) => (
                  <option key={room.id} value={room.id}>
                    {room.code} - {room.building_name}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <label className="space-y-1">
            <span className="text-xs font-medium text-slate-500">Người thuê</span>
            <select
              className="h-10 w-full rounded-md border border-border bg-white px-3 text-sm"
              defaultValue={contract?.tenant_id ?? ""}
              disabled={lockedByInvoice}
              name="tenant_id"
              required
            >
              <option value="">Chọn người thuê</option>
              {tenants.map((tenant) => (
                <option key={tenant.id} value={tenant.id}>
                  {tenant.tenant_code} - {tenant.full_name}
                </option>
              ))}
            </select>
          </label>
          <Field
            defaultValue={contract?.start_date}
            disabled={lockedByInvoice}
            label="Ngày bắt đầu"
            name="start_date"
            required
            type="date"
          />
          <Field defaultValue={contract?.end_date} label="Ngày kết thúc" name="end_date" type="date" />
          <Field
            defaultValue={contract?.monthly_rent}
            disabled={lockedByInvoice}
            label="Tiền thuê"
            name="monthly_rent"
            required
            type="number"
          />
          <Field
            defaultValue={contract?.deposit_amount}
            disabled={lockedByInvoice}
            label="Tiền cọc"
            name="deposit_amount"
            type="number"
          />
        </div>
      </Card>

      <Card>
        <label className="space-y-1">
          <span className="text-xs font-medium text-slate-500">Ghi chú</span>
          <textarea
            className="min-h-24 w-full rounded-md border border-border px-3 py-2 text-sm"
            defaultValue={contract?.note ?? ""}
            name="note"
          />
        </label>
      </Card>

      {error ? <p className="text-sm text-rose-600">{error}</p> : null}
      <Button type="submit">
        <Save className="size-4" />
        Lưu hợp đồng
      </Button>
    </form>
  );
}

function Field({
  defaultValue,
  disabled,
  label,
  name,
  required,
  type = "text",
}: {
  defaultValue?: string | number | null;
  disabled?: boolean;
  label: string;
  name: string;
  required?: boolean;
  type?: "text" | "date" | "number";
}) {
  return (
    <label className="space-y-1">
      <span className="text-xs font-medium text-slate-500">{label}</span>
      <Input
        defaultValue={defaultValue ?? ""}
        disabled={disabled}
        min={type === "number" ? 0 : undefined}
        name={name}
        required={required}
        type={type}
      />
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

function numberOrNull(value: FormDataEntryValue | null) {
  const text = String(value || "").trim();
  return text.length > 0 ? Number(text) : null;
}
