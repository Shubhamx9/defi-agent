import { atom } from "recoil";

export const openState = atom<boolean>({
  key: "openState",
  default: true,
});