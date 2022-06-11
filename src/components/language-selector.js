/* eslint-disable prettier/prettier */
import React from 'react';

import SelectDropdown from 'react-native-select-dropdown';

const languages = [
  {
    label: 'English',
    value: 'en',
  },
  {
    label: 'Romanian',
    value: 'ro',
  },
  {
    label: 'German',
    value: 'de',
  },
  {
    label: 'French',
    value: 'fr',
  },
  {
    label: 'Italian',
    value: 'it',
  },
  {
    label: 'Spanish',
    value: 'es',
  },
  {
    label: 'Greek',
    value: 'el',
  },
];

const LanguageSelector = ({setLanguage}) => {
  return (
    <SelectDropdown
      data={languages}
      onSelect={(selectedItem) => setLanguage(selectedItem.value)}
      buttonTextAfterSelection={(selectedItem) => selectedItem.label }
      rowTextForSelection={(item) => item.label}
    />
  );
};

export default LanguageSelector;
