/* eslint-disable prettier/prettier */
import React, {useState} from 'react';
import {
  ActivityIndicator,
  SafeAreaView,
  StatusBar,
  Text,
  Button,
} from 'react-native';
import {API} from 'aws-amplify';

const myAPI = 'api0a629dfb';
const path = '/translate';

const HomeScreen = (props) => {

  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState('');

  const callBackEnd = async () => {
    setLoading(true);
    try {
      const res = await API.post(myAPI, path);
      setLoading(false);
      console.log(res);
      setOutput(res);
    }
    catch (error) {
      console.log(error);
      setLoading(false);
    }
  };

  return (
    <>
      <StatusBar barStyle="dark-content" />
      <SafeAreaView>
        <Text>Home</Text>

        <Button onPress={() => callBackEnd()} title='Test backend' />
        <ActivityIndicator animating={loading} size='large' color='#000000' />

        <Text>{output}</Text>

      </SafeAreaView>
    </>
  );
};

export default HomeScreen;
