import React, { createContext, useContext, useState, useEffect, ReactNode, useMemo } from 'react';
import { ALL_LOCALES, LocaleDefinition } from './languages';
import { TRANSLATIONS } from './translations';

interface I18nContextType {
  currentLocale: string;
  setLocale: (code: string) => void;
  activeLocaleDef: LocaleDefinition;
  t: (key: string, defaultText?: string) => string;
  isRtl: boolean;
  locales: LocaleDefinition[];
  totalLocalesCount: number;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export const I18nProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentLocale, setCurrentLocaleState] = useState<string>(() => {
    return localStorage.getItem('fujinova_locale') || 'en';
  });

  const activeLocaleDef = useMemo(() => {
    return ALL_LOCALES.find(l => l.code === currentLocale) || ALL_LOCALES[0];
  }, [currentLocale]);

  const isRtl = activeLocaleDef.dir === 'rtl';

  useEffect(() => {
    localStorage.setItem('fujinova_locale', currentLocale);
    document.documentElement.dir = isRtl ? 'rtl' : 'ltr';
    document.documentElement.lang = currentLocale;
  }, [currentLocale, isRtl]);

  const setLocale = (code: string) => {
    setCurrentLocaleState(code);
  };

  const t = (key: string, defaultText?: string): string => {
    const localeDict = TRANSLATIONS[currentLocale];
    if (localeDict && localeDict[key]) {
      return localeDict[key];
    }
    const enDict = TRANSLATIONS['en'];
    if (enDict && enDict[key]) {
      return enDict[key];
    }
    return defaultText || key;
  };

  return (
    <I18nContext.Provider
      value={{
        currentLocale,
        setLocale,
        activeLocaleDef,
        t,
        isRtl,
        locales: ALL_LOCALES,
        totalLocalesCount: ALL_LOCALES.length
      }}
    >
      {children}
    </I18nContext.Provider>
  );
};

export const useI18n = (): I18nContextType => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};
