/* eslint-disable prettier/prettier */
import React from 'react';
import {SafeAreaView, StatusBar, Text} from 'react-native';

const HomeScreen = (props) => {
  return (
    <>
      <StatusBar barStyle="dark-content" />
      <SafeAreaView>
        <Text>Home</Text>
      </SafeAreaView>
    </>
  );
};

export default HomeScreen;
