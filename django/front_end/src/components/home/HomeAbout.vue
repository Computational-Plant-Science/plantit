<template>
    <div id="background">
        <b-container id="main">
            <b-row>
                <b-col>
                    <b-img
                        :src="require('@/assets/logo.png')"
                        width="100px"
                        alt="Plant IT"
                    ></b-img>
                    <h1>PLANT IT</h1>
                    <b-jumbotron id="message">
                        Plant IT empowers computational researchers to make
                        their algorithms available to a broad community, and
                        provides biological researchers with an easy-to-use
                        interface to apply the algorithms to their own data.
                    </b-jumbotron>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
export default {
    name: 'HomeAbout'
};
</script>

<style scoped lang="sass">
#background
  background-image: url('../../assets/frontpage/index_bg.png')
  background-repeat: no-repeat
  background-position: bottom
  background-size: 100%

#main
  text-align: center
  padding-bottom: 50px

#message
  width: 50%
  background-color: gray
  margin: 0 auto
  color: white
</style>
