export const tenantStatuses = [
  ["not_renting", "Chưa thuê"],
  ["active", "Đang thuê"],
  ["left", "Đã rời đi"],
  ["deleted", "Đã xóa"],
] as const;

export function tenantStatusLabel(status: string) {
  return tenantStatuses.find(([value]) => value === status)?.[1] ?? status;
}

export function tenantStatusTone(status: string): "green" | "amber" | "red" | "slate" {
  if (status === "active") return "green";
  if (status === "deleted") return "red";
  if (status === "left") return "amber";
  return "slate";
}

export function genderLabel(gender?: string | null) {
  if (gender === "male") return "Nam";
  if (gender === "female") return "Nữ";
  if (gender === "other") return "Khác";
  return "Chưa khai báo";
}

export function identityTypeLabel(identityType?: string | null) {
  if (identityType === "cccd") return "CCCD";
  if (identityType === "cmnd") return "CMND";
  if (identityType === "passport") return "Passport";
  return "Chưa khai báo";
}
