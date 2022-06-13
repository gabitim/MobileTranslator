/* eslint-disable prettier/prettier */
import React from 'react';

import FontAwesome from 'react-native-vector-icons/FontAwesome';
import {StyleSheet} from 'react-native';
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
      defaultButtonText="Destination language"
      buttonStyle={styles.destinationLanguageButton}
      buttonTextStyle={styles.destinationLanguageButtonText}
      renderDropdownIcon={isOpened => {
        return <FontAwesome name={isOpened ? 'chevron-up' : 'chevron-down'} color={'#444'} size={18} />;
      }}
      dropdownIconPosition={'right'}
      data={languages}
      onSelect={(selectedItem) => setLanguage(selectedItem.value)}
      buttonTextAfterSelection={(selectedItem) => selectedItem.label }
      rowTextForSelection={(item) => item.label}
    />
  );
};

const styles = StyleSheet.create({
  destinationLanguageButton: {
    width: 220,
    backgroundColor: '#0099ff',
    alignSelf: 'center',
  },
  destinationLanguageButtonText: {
    color: '#ffffff',
  },
});

export default LanguageSelector;
