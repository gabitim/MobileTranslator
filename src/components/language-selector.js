/* eslint-disable prettier/prettier */
import React from 'react';

import FontAwesome from 'react-native-vector-icons/FontAwesome';
import {StyleSheet} from 'react-native';
import SelectDropdown from 'react-native-select-dropdown';

export const languages = [
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
      defaultButtonText="Language"
      buttonStyle={styles.destinationLanguageButton}
      buttonTextStyle={styles.destinationLanguageButtonText}
      renderDropdownIcon={isOpened => {
        return <FontAwesome name={isOpened ? 'chevron-up' : 'chevron-down'} color={'#444'} size={18} />;
      }}
      dropdownIconPosition={'right'}
      data={languages}
      defaultValue={languages[0]}
      onSelect={(selectedItem) => setLanguage(selectedItem.value)}
      buttonTextAfterSelection={(selectedItem) => selectedItem.label }
      rowTextForSelection={(item) => item.label}
    />
  );
};

const styles = StyleSheet.create({
  destinationLanguageButton: {
    borderRadius: 5,
    width: 130,
    height: 40,
    backgroundColor: 'gray',
    alignSelf: 'center',
  },
  destinationLanguageButtonText: {
    color: 'white',
    fontSize: 14,
  },
});

export default LanguageSelector;
