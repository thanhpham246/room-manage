export const contractStatuses = [
  ["pending", "Sắp hiệu lực"],
  ["active", "Đang hiệu lực"],
  ["ended", "Đã kết thúc"],
  ["terminated", "Chấm dứt sớm"],
  ["cancelled", "Đã hủy"],
  ["deleted", "Đã xóa"],
] as const;

export function contractStatusLabel(status: string) {
  return contractStatuses.find(([value]) => value === status)?.[1] ?? status;
}

export function contractStatusTone(status: string): "green" | "amber" | "red" | "slate" {
  if (status === "active") return "green";
  if (status === "pending") return "amber";
  if (status === "terminated" || status === "cancelled" || status === "deleted") return "red";
  return "slate";
}

export function contractScopeLabel(scope: string) {
  if (scope === "whole_building") return "Nhà nguyên căn";
  return "Phòng";
}
