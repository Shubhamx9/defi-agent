import { atom } from "recoil";

// A helper to persist atom state to localStorage
const localStorageEffect =
  <T>(key: string) =>
  ({ setSelf, onSet }: any) => {
    if (typeof window !== "undefined") {
      const savedValue = localStorage.getItem(key);
      if (savedValue != null) {
        setSelf(JSON.parse(savedValue));
      }

      onSet((newValue: T, _: T, isReset: boolean) => {
        if (isReset) {
          localStorage.removeItem(key);
        } else {
          localStorage.setItem(key, JSON.stringify(newValue));
        }
      });
    }
  };

export const darkModeState = atom<boolean>({
  key: "darkModeState",
  default: true,
  effects: [localStorageEffect("darkMode")],
});
